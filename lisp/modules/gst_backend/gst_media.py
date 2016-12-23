# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
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
from lisp.core.has_properties import Property
from lisp.modules.gst_backend import elements
from lisp.modules.gst_backend.gi_repository import Gst


def validate_pipeline(pipe, rebuild=False):
    # The first must be an input element
    if pipe[0] not in elements.inputs().keys():
        return False

    # The middle elements must be plugins elements
    if rebuild:
        if not isinstance(pipe, list):
            pipe = list(pipe)

        pipe[1:-1] = set(pipe[1:-1]).intersection(
            set(elements.plugins().keys()))
    else:
        if len(set(pipe[1:-1]) - set(elements.plugins().keys())) != 0:
            return False

    # The last must be an output element
    if pipe[-1] not in elements.outputs().keys():
        return False

    return pipe if rebuild else True


class GstMedia(Media):
    """Media implementation based on the GStreamer framework."""

    pipe = Property(default=())

    def __init__(self):
        super().__init__()

        self._state = MediaState.Null
        self._elements = []
        self._old_pipe = ''
        self._loop_count = 0

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
                         self._elements)

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
            elements_properties = self.elements_properties()
            self.__build_pipeline()
            self.update_elements(elements_properties)

            self._elements[0].changed('duration').connect(
                self.__duration_changed)
            self.__duration_changed(self._elements[0].duration)

    def current_time(self):
        ok, position = self._gst_pipe.query_position(Gst.Format.TIME)
        return position // Gst.MSECOND if ok else 0

    def play(self):
        if self.state == MediaState.Stopped or self.state == MediaState.Paused:
            self.on_play.emit(self)

            for element in self._elements:
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

            for element in self._elements:
                element.pause()

            self._state = MediaState.Paused
            self._gst_pipe.set_state(Gst.State.PAUSED)
            self._gst_pipe.get_state(Gst.SECOND)

            # FIXME: the pipeline is not flushed (fucking GStreamer)

            self.paused.emit(self)

    def stop(self):
        if self.state == MediaState.Playing or self.state == MediaState.Paused:
            self.on_stop.emit(self)

            for element in self._elements:
                element.stop()

            self.interrupt(emit=False)
            self.stopped.emit(self)

    def __seek(self, position):
        # FIXME: not working when in pause (fix or disallow)
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
        for element in self._elements:
            if type(element).__name__ == class_name:
                return element

    def elements(self):
        return self._elements.copy()

    def elements_properties(self, only_changed=False):
        properties = {}

        for element in self._elements:
            e_properties = element.properties(only_changed)
            if e_properties:
                properties[type(element).__name__] = e_properties

        return properties

    def input_uri(self):
        try:
            return self._elements[0].input_uri()
        except Exception:
            pass

    def interrupt(self, dispose=False, emit=True):
        for element in self._elements:
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

    def properties(self, only_changed=False):
        properties = super().properties(only_changed).copy()
        properties['elements'] = self.elements_properties(only_changed)
        return properties

    def update_elements(self, properties):
        for element in self._elements:
            if type(element).__name__ in properties:
                element.update_properties(properties[type(element).__name__])

    def update_properties(self, properties):
        elements_properties = properties.pop('elements', {})
        super().update_properties(properties)

        self.update_elements(elements_properties)

        if self.state == MediaState.Null or self.state == MediaState.Error:
            self._state = MediaState.Stopped

    @staticmethod
    def _pipe_elements():
        tmp = {}
        tmp.update(elements.inputs())
        tmp.update(elements.outputs())
        tmp.update(elements.plugins())
        return tmp

    def __append_element(self, element):
        if self._elements:
            self._elements[-1].link(element)

        self._elements.append(element)

    def __remove_element(self, index):
        if index > 0:
            self._elements[index - 1].unlink(self._elements[index])
        if index < len(self._elements) - 1:
            self._elements[index - 1].link(self._elements[index + 1])
            self._elements[index].unlink(self._elements[index])

        self._elements.pop(index).dispose()

    def __build_pipeline(self):
        # Set to NULL the pipeline
        self.interrupt(dispose=True)
        # Remove all pipeline children
        for __ in range(self._gst_pipe.get_children_count()):
            self._gst_pipe.remove(self._gst_pipe.get_child_by_index(0))
        # Remove all the elements
        for __ in range(len(self._elements)):
            self.__remove_element(len(self._elements) - 1)

        # Create all the new elements
        pipe_elements = self._pipe_elements()
        for element in self.pipe:
            self.__append_element(pipe_elements[element](self._gst_pipe))

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

        for element in media_elements:
            element.dispose()
