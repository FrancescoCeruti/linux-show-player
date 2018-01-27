# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2018 Francesco Ceruti <ceppofrancy@gmail.com>
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

import weakref

from lisp.backend.media import Media, MediaState
from lisp.core.has_properties import HasProperties
from lisp.core.properties import Property, WriteOnceProperty
from lisp.plugins.gst_backend import elements as gst_elements
from lisp.plugins.gst_backend.gi_repository import Gst


def validate_pipeline(pipe, rebuild=False):
    # The first must be an input element
    if pipe[0] not in gst_elements.inputs().keys():
        return False

    # The middle elements must be plugins elements
    if rebuild:
        if not isinstance(pipe, list):
            pipe = list(pipe)

        pipe[1:-1] = set(pipe[1:-1]).intersection(
            set(gst_elements.plugins().keys()))
    else:
        if len(set(pipe[1:-1]) - set(gst_elements.plugins().keys())) != 0:
            return False

    # The last must be an output element
    if pipe[-1] not in gst_elements.outputs().keys():
        return False

    return pipe if rebuild else True


class GstMedia(Media):
    """Media implementation based on the GStreamer framework."""

    pipe = Property(default=())
    elements = Property(default=None)

    def __init__(self):
        super().__init__()

        self._state = MediaState.Null
        self._old_pipe = ''
        self._loop_count = 0

        self.elements = GstMediaElements()
        self._gst_pipe = Gst.Pipeline()
        self._gst_state = Gst.State.NULL
        self._time_query = Gst.Query.new_position(Gst.Format.TIME)

        bus = self._gst_pipe.get_bus()
        bus.add_signal_watch()

        # Use a weakref instead of the method or the object will not be
        # garbage-collected
        on_message = weakref.WeakMethod(self.__on_message)
        handler = bus.connect('message', lambda *args: on_message()(*args))
        weakref.finalize(self, self.__finalizer, self._gst_pipe, handler,
                         self.elements)

        self.changed('loop').connect(self.__prepare_loops)
        self.changed('pipe').connect(self.__prepare_pipe)

    @Media.state.getter
    def state(self):
        return self._state

    def __prepare_loops(self, loops):
        self._loop_count = loops

    def __prepare_pipe(self, pipe):
        if pipe != self._old_pipe:
            self._old_pipe = pipe

            # If the pipeline is invalid raise an error
            pipe = validate_pipeline(pipe, rebuild=True)
            if not pipe:
                raise ValueError('Invalid pipeline "{0}"'.format(pipe))

            # Build the pipeline
            ep_copy = self.elements.properties()
            self.__build_pipeline()
            self.elements.update_properties(ep_copy)

            self.elements[0].changed('duration').connect(
                self.__duration_changed)
            self.__duration_changed(self.elements[0].duration)

    def current_time(self):
        ok, position = self._gst_pipe.query_position(Gst.Format.TIME)
        return position // Gst.MSECOND if ok else 0

    def play(self):
        if self.state == MediaState.Stopped or self.state == MediaState.Paused:
            self.on_play.emit(self)

            for element in self.elements:
                element.play()

            self._state = MediaState.Playing
            self._gst_pipe.set_state(Gst.State.PLAYING)
            self._gst_pipe.get_state(Gst.SECOND)

            if self.start_time > 0 or self.stop_time > 0:
                self.seek(self.start_time)

            self.played.emit(self)

    def pause(self):
        if self.state == MediaState.Playing:
            self.on_pause.emit(self)

            for element in self.elements:
                element.pause()

            self._state = MediaState.Paused
            self._gst_pipe.set_state(Gst.State.PAUSED)
            self._gst_pipe.get_state(Gst.SECOND)

            # FIXME: the pipeline is not flushed (fucking GStreamer)

            self.paused.emit(self)

    def stop(self):
        if self.state == MediaState.Playing or self.state == MediaState.Paused:
            self.on_stop.emit(self)

            for element in self.elements:
                element.stop()

            self.interrupt(emit=False)
            self.stopped.emit(self)

    def __seek(self, position):
        if self.state == MediaState.Playing or self.state == MediaState.Paused:
            max_position = self.duration
            if 0 < self.stop_time < self.duration:
                max_position = self.stop_time

            if position < max_position:
                # Query segment info for the playback rate
                query = Gst.Query.new_segment(Gst.Format.TIME)
                self._gst_pipe.query(query)
                rate = Gst.Query.parse_segment(query)[0]

                # Check stop_position value
                stop_type = Gst.SeekType.NONE
                if self.stop_time > 0:
                    stop_type = Gst.SeekType.SET

                # Seek the pipeline
                result = self._gst_pipe.seek(
                    rate if rate > 0 else 1,
                    Gst.Format.TIME,
                    Gst.SeekFlags.FLUSH,
                    Gst.SeekType.SET,
                    position * Gst.MSECOND,
                    stop_type,
                    self.stop_time * Gst.MSECOND)

                return result

        return False

    def seek(self, position):
        if self.__seek(position):
            self.sought.emit(self, position)

    def element(self, class_name):
        return getattr(self.elements, class_name, None)

    def input_uri(self):
        try:
            return self.elements[0].input_uri()
        except Exception:
            pass

    def interrupt(self, dispose=False, emit=True):
        for element in self.elements:
            element.interrupt()

        state = self._state

        self._gst_pipe.set_state(Gst.State.NULL)
        if dispose:
            self._state = MediaState.Null
        else:
            self._gst_pipe.set_state(Gst.State.READY)
            self._state = MediaState.Stopped

        self._loop_count = self.loop

        if emit and (state == MediaState.Playing or
                     state == MediaState.Paused):
            self.interrupted.emit(self)

    def update_properties(self, properties):
        # In order to update the other properties we need the pipeline
        pipe = properties.pop('pipe', None)
        if pipe:
            self.pipe = pipe

        super().update_properties(properties)

        if self.state == MediaState.Null or self.state == MediaState.Error:
            self._state = MediaState.Stopped

    def __build_pipeline(self):
        # Set to NULL the pipeline
        self.interrupt(dispose=True)

        # Remove all pipeline children
        for __ in range(self._gst_pipe.get_children_count()):
            self._gst_pipe.remove(self._gst_pipe.get_child_by_index(0))

        # Remove all the elements
        self.elements.clear()

        # Create all the new elements
        all_elements = gst_elements.all_elements()
        for element in self.pipe:
            self.elements.append(all_elements[element](self._gst_pipe))

        # Set to Stopped/READY the pipeline
        self._state = MediaState.Stopped
        self._gst_pipe.set_state(Gst.State.READY)

        self.elements_changed.emit(self)

    def __on_message(self, bus, message):
        if message.src == self._gst_pipe:
            if message.type == Gst.MessageType.STATE_CHANGED:
                self._gst_state = message.parse_state_changed()[1]
            elif message.type == Gst.MessageType.EOS:
                self.__on_eos()
            elif message.type == Gst.MessageType.CLOCK_LOST:
                self._gst_pipe.set_state(Gst.State.PAUSED)
                self._gst_pipe.set_state(Gst.State.PLAYING)

        if message.type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            self._state = MediaState.Error
            self.interrupt(dispose=True, emit=False)
            self.error.emit(self, str(err), str(debug))

    def __on_eos(self):
        if self._loop_count != 0:
            self._loop_count -= 1
            self.seek(self.start_time)
        else:
            self._state = MediaState.Stopped
            self.eos.emit(self)
            self.interrupt(emit=False)

    def __duration_changed(self, duration):
        self.duration = duration

    @staticmethod
    def __finalizer(pipeline, connection_handler, media_elements):
        # Allow pipeline resources to be released
        pipeline.set_state(Gst.State.NULL)

        bus = pipeline.get_bus()
        bus.remove_signal_watch()
        bus.disconnect(connection_handler)

        media_elements.clear()


def GstMediaElements():
    return type('GstMediaElements', (_GstMediaElements, ), {})()


class _GstMediaElements(HasProperties):

    def __init__(self):
        super().__init__()
        self.elements = []

    def __getitem__(self, index):
        return self.elements[index]

    def __len__(self):
        return len(self.elements)

    def __contains__(self, item):
        return item in self.elements

    def __iter__(self):
        return iter(self.elements)

    def append(self, element):
        """
        :type element: lisp.backend.media_element.MediaElement
        """
        if self.elements:
            self.elements[-1].link(element)
        self.elements.append(element)

        # Add a property for the new added element
        self.register_property(
            element.__class__.__name__,
            WriteOnceProperty(default=None)
        )
        setattr(self, element.__class__.__name__, element)

    def remove(self, element):
        self.pop(self.elements.index(element))

    def pop(self, index):
        if index > 0:
            self.elements[index - 1].unlink(self.elements[index])
        if index < len(self.elements) - 1:
            self.elements[index].unlink(self.elements[index + 1])
            self.elements[index - 1].link(self.elements[index + 1])

        element = self.elements.pop(index)
        element.dispose()

        # Remove the element corresponding property
        self.remove_property(element.__class__.__name__)

    def clear(self):
        while self.elements:
            self.pop(len(self.elements) - 1)
