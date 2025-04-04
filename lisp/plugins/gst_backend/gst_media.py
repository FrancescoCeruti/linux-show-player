# This file is part of Linux Show Player
#
# Copyright 2024 Francesco Ceruti <ceppofrancy@gmail.com>
#
# Linux Show Player is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Linux Show Player is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Linux Show Player.  If not, see <http://www.gnu.org/licenses/>.

import logging
import weakref

from lisp.backend.media import Media, MediaState
from lisp.backend.media_element import MediaType, ElementType
from lisp.core.properties import Property
from lisp.core.util import weak_call_proxy
from lisp.plugins.gst_backend import elements as gst_elements
from lisp.plugins.gst_backend.gi_repository import Gst
from lisp.plugins.gst_backend.gst_element import GstMediaElements
from lisp.plugins.gst_backend.gst_utils import GstError
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)


GST_TO_MEDIA_STATE = {
    Gst.State.NULL: MediaState.Null,
    Gst.State.READY: MediaState.Ready,
    Gst.State.PAUSED: MediaState.Paused,
    Gst.State.PLAYING: MediaState.Playing,
}


def media_finalizer(pipeline, message_handler, media_elements):
    # Allow pipeline resources to be released
    pipeline.set_state(Gst.State.NULL)

    # Disconnect message handler
    bus = pipeline.get_bus()
    bus.remove_signal_watch()
    bus.disconnect(message_handler)

    # Dispose all the elements
    media_elements.clear()


class GstMedia(Media):
    """Media implementation based on the GStreamer framework."""

    pipe = Property(default=())
    elements = Property(default=GstMediaElements.class_defaults())

    def __init__(self):
        super().__init__()
        self.elements = GstMediaElements()

        self.__pipeline = None
        self.__finalizer = None
        self.__loop = 0  # current number of loops left to do
        self.__current_pipe = None  # A copy of the pipe property

        self.changed("loop").connect(self.__on_loops_changed)
        self.changed("pipe").connect(self.__on_pipe_changed)

    @Media.state.getter
    def state(self):
        if self.__pipeline is None:
            return MediaState.Null

        return GST_TO_MEDIA_STATE.get(
            self.__pipeline.get_state(Gst.MSECOND)[1], MediaState.Null
        )

    def current_time(self):
        if self.__pipeline is not None:
            ok, position = self.__pipeline.query_position(Gst.Format.TIME)
            return position // Gst.MSECOND if ok else 0

        return 0

    def play(self):
        if self.state == MediaState.Null:
            self.__init_pipeline()

        if self.state == MediaState.Ready or self.state == MediaState.Paused:
            self.on_play.emit(self)

            for element in self.elements:
                element.play()

            if self.state != MediaState.Paused:
                self.__pipeline.set_state(Gst.State.PAUSED)
                self.__pipeline.get_state(Gst.SECOND)
                self.__seek(self.start_time)
            else:
                self.__seek(self.current_time())

            self.__pipeline.set_state(Gst.State.PLAYING)
            self.__pipeline.get_state(Gst.SECOND)

            self.played.emit(self)

    def pause(self):
        if self.state == MediaState.Playing:
            self.on_pause.emit(self)

            for element in self.elements:
                element.pause()

            self.__pipeline.set_state(Gst.State.PAUSED)
            self.__pipeline.get_state(Gst.SECOND)

            # Flush the pipeline
            self.__seek(self.current_time())

            self.paused.emit(self)

    def stop(self):
        if self.state == MediaState.Playing or self.state == MediaState.Paused:
            self.on_stop.emit(self)

            for element in self.elements:
                element.stop()

            self.__pipeline.set_state(Gst.State.READY)
            self.__pipeline.get_state(Gst.SECOND)
            self.__reset_media()

            self.stopped.emit(self)

    def seek(self, position):
        if self.__seek(position):
            self.sought.emit(self, position)

    def loop_release(self):
        self.__loop = 0

    def element(self, class_name):
        return getattr(self.elements, class_name, None)

    def input_uri(self):
        try:
            return self.elements[0].input_uri()
        except (IndexError, AttributeError):
            pass

    def update_properties(self, properties):
        # In order to update the other properties we need the pipeline first
        pipe = properties.pop("pipe", ())
        if pipe:
            self.pipe = pipe

        super().update_properties(properties)

    def __reset_media(self):
        self.__loop = self.loop

    def __segment_stop_position(self):
        if 0 < self.stop_time < self.duration:
            return self.stop_time

        return self.duration

    def __seek(self, position, flush=True):
        if (
            self.state not in (MediaState.Playing, MediaState.Paused)
            or position > self.__segment_stop_position()
        ):
            return False

        # Query segment info for the playback rate
        query = Gst.Query.new_segment(Gst.Format.TIME)
        self.__pipeline.query(query)
        rate = Gst.Query.parse_segment(query)[0]

        # Check if we need to set an early stop position
        if self.stop_time > 0:
            stop_type = Gst.SeekType.SET
        else:
            stop_type = Gst.SeekType.NONE

        # Decide which SeekFlags we want to use
        flags = Gst.SeekFlags.TRICKMODE

        # We want to receive SEGMENT_DONE messages, allowing seamless loops,
        # except for the "last" loop, were we want to receive a normal EOS
        # to ensure that all pipeline buffers have been processed.
        if self.__loop != 0:
            flags |= Gst.SeekFlags.SEGMENT

        # While seeking, we typically want to flush any buffered data. However,
        # there are exceptions, such as during seamless looping, where flushing is undesirable.
        if flush:
            flags |= Gst.SeekFlags.FLUSH

        # Seek the pipeline
        return self.__pipeline.seek(
            rate if rate > 0 else 1,
            Gst.Format.TIME,
            flags,
            Gst.SeekType.SET,
            position * Gst.MSECOND,
            stop_type,
            self.stop_time * Gst.MSECOND,
        )

    def __on_loops_changed(self, loops):
        self.__loop = loops

    def __on_pipe_changed(self, new_pipe):
        # Rebuild the pipeline only if something is changed
        if new_pipe != self.__current_pipe:
            self.__current_pipe = new_pipe
            self.__init_pipeline()

    def __init_pipeline(self):
        # Make a copy of the current elements properties
        elements_properties = self.elements.properties()

        # Call the current media-finalizer, if any
        if self.__finalizer is not None:
            # Set pipeline to NULL, finalize bus-handler and elements
            self.__finalizer()

        self.__pipeline = Gst.Pipeline()
        # Add a callback to watch for pipeline bus-messages
        bus = self.__pipeline.get_bus()
        bus.add_signal_watch()
        # Use a weakref or GStreamer will hold a reference of the callback
        handler = bus.connect(
            "message", weak_call_proxy(weakref.WeakMethod(self.__on_message))
        )

        # Create all the new elements
        all_elements = gst_elements.all_elements()
        for element in self.pipe:
            try:
                self.elements.append(all_elements[element](self.__pipeline))
            except KeyError:
                logger.warning(
                    translate(
                        "GstMediaWarning", 'Invalid pipeline element: "{}"'
                    ).format(element)
                )
            except Exception:
                logger.warning(
                    translate(
                        "GstMediaError", 'Cannot create pipeline element: "{}"'
                    ).format(element),
                    exc_info=True,
                )

        # Collect audio/video elements
        audio_elements = self.find_audio_elements()
        video_elements = self.find_video_elements()

        # Input source
        self.source_element = self.elements[0]

        # Link audio/video paths
        if audio_elements:
            for index, ele in enumerate(audio_elements):
                if index == 0:
                    self.source_element.audio_convert.link(ele.sink())
                else: 
                    self.elements[index].link(ele)

        if video_elements:
            for index, ele in enumerate(video_elements):
                if index == 0:
                    self.source_element.video_convert.link(ele.sink())
                else: 
                    self.elements[-1].link(ele.sink())

        # Reload the elements properties
        self.elements.update_properties(elements_properties)

        # The source element should provide the duration
        self.source_element.changed("duration").connect(self.__duration_changed)
        self.duration = self.source_element.duration

        # Create a new finalizer object to free the pipeline when the media
        # is dereferenced
        self.__finalizer = weakref.finalize(
            self, media_finalizer, self.__pipeline, handler, self.elements
        )

        # Set the pipeline to READY
        self.__pipeline.set_state(Gst.State.READY)
        self.__pipeline.get_state(Gst.SECOND)

        self.elements_changed.emit(self)

    def __on_message(self, bus, message):
        if message.src == self.__pipeline:
            if message.type == Gst.MessageType.SEGMENT_DONE:
                if self.__loop != 0:
                    # If we still have loops to do then seek to start
                    self.__loop -= 1
                    self.__seek(self.start_time, flush=False)
                else:
                    # We reached loop 0 earlier (e.g. due to a loop-release).
                    # We cannot stop the pipeline yet, likely there's still data in the buffers,
                    # to "force" an EOS event we seek to the end of the stream, without flushing.
                    self.__seek(self.__segment_stop_position(), flush=False)

            elif message.type == Gst.MessageType.EOS:
                self.__pipeline.set_state(Gst.State.READY)
                self.__pipeline.get_state(Gst.SECOND)

                for element in self.elements:
                    element.eos()

                self.__reset_media()
                self.eos.emit(self)

            elif message.type == Gst.MessageType.CLOCK_LOST:
                self.__pipeline.set_state(Gst.State.PAUSED)
                self.__pipeline.set_state(Gst.State.PLAYING)

        if message.type == Gst.MessageType.ERROR:
            error, debug = message.parse_error()
            logger.error(
                f"GStreamer: {error.message}", exc_info=GstError(debug)
            )

            # Set the pipeline to NULL
            self.__pipeline.set_state(Gst.State.NULL)
            self.__pipeline.get_state(Gst.SECOND)
            self.__reset_media()

            self.error.emit(self)

    def __duration_changed(self, duration):
        self.duration = duration

    def find_audio_elements(self):
        eles = []
        for ele in self.elements:
            if ele.MediaType is MediaType.Audio:
                eles.append(ele)
        return eles
    
    def find_video_elements(self):
        eles = []
        for ele in self.elements:
            if ele.MediaType is MediaType.Video:
                eles.append(ele)
        return eles