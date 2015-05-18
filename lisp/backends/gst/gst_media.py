# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2015 Francesco Ceruti <ceppofrancy@gmail.com>
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

from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from os import path, cpu_count as _cpu_count
from re import match

from lisp.backends.base.media import Media, MediaState, when_playing
from lisp.backends.gst.gi_repository import Gst
from lisp.backends.gst import elements
from lisp.backends.gst.gst_utils import gst_uri_duration
from lisp.core.decorators import async_in_pool, check_state
from lisp.utils.util import type_check


def cpu_count():
    return _cpu_count() if _cpu_count() is not None else 1


def gst_pipe_regex():
    return ('^(' + '!|'.join(elements.inputs().keys()) + '!)' +
            '(' + '!|'.join(elements.plugins().keys()) + '!)*' +
            '(' + '|'.join(elements.outputs().keys()) + ')$')


class GstMedia(Media):
    """Media implementation based on the GStreamer framework."""
    _properties_ = ['duration', 'start_at', 'loop', 'pipe', '_mtime']
    _properties_.extend(Media._properties_)

    def __init__(self):
        super().__init__()

        self.duration = 0
        self.start_at = 0
        self._mtime = -1
        self.__pipe = ''
        self.__loop = 0

        self._elements = []
        self._old_pipe = ''
        self._loop_count = 0

        self._gst_pipe = Gst.Pipeline()
        self._gst_state = Gst.State.NULL

        self.__bus = self._gst_pipe.get_bus()
        self.__bus.add_signal_watch()
        self.__bus.connect('message', self.__on_message)

    @property
    def loop(self):
        return self.__loop

    @loop.setter
    def loop(self, value):
        type_check(value, int)

        self.__loop = value if value >= -1 else -1
        self._loop_count = self.__loop

    @property
    def pipe(self):
        return self.__pipe

    @pipe.setter
    def pipe(self, pipe):
        if pipe != self.__pipe:
            # Remove whitespace
            pipe = pipe.replace(' ', '')
            # If the syntax is invalid raise an error
            if match(gst_pipe_regex(), pipe) is None:
                raise ValueError('invalid pipeline syntax: {0}'.format(pipe))
            # TODO: I don't like this
            # Remove duplicated elements and set the value
            self.__pipe = '!'.join(OrderedDict.fromkeys(pipe.split('!')))

            # Build the pipeline
            self.__build_pipeline()

            if 'uri' in self._elements[0]._properties_:
                self._elements[0].changed('uri').connect(self.__uri_changed)

    def current_time(self):
        if self._gst_state in (Gst.State.PLAYING, Gst.State.PAUSED):
            return (self._gst_pipe.query_position(Gst.Format.TIME)[1] //
                    Gst.MSECOND)
        return -1

    @check_state(MediaState.Stopped, MediaState.Paused)
    def play(self):
        self.on_play.emit(self)

        self.state = MediaState.Playing
        self._gst_pipe.set_state(Gst.State.PLAYING)
        self._gst_pipe.get_state(Gst.SECOND)

        self.played.emit(self)

    @when_playing
    def pause(self):
        self.on_pause.emit(self)

        for element in self._elements:
            element.pause()

        self.state = MediaState.Paused
        self._gst_pipe.set_state(Gst.State.PAUSED)
        self._gst_pipe.get_state(Gst.SECOND)

        self.paused.emit(self)

    @check_state(MediaState.Playing, MediaState.Paused)
    def stop(self):
        self.on_stop.emit(self)

        for element in self._elements:
            element.stop()

        self.interrupt(emit=False)
        self.stopped.emit(self)

    @check_state(MediaState.Playing, MediaState.Paused)
    def seek(self, position):
        if position < self.duration:
            # Query segment info for the playback rate
            query = Gst.Query.new_segment(Gst.Format.TIME)
            self._gst_pipe.query(query)
            rate = Gst.Query.parse_segment(query)[0]

            # Seek the pipeline
            self._gst_pipe.seek(rate if rate > 0 else 1,
                                Gst.Format.TIME,
                                Gst.SeekFlags.FLUSH,
                                Gst.SeekType.SET,
                                position * Gst.MSECOND,
                                Gst.SeekType.NONE,
                                -1)

            self.sought.emit(self, position)

    def element(self, name):
        for element in self._elements:
            if element.Name == name:
                return element

    def elements(self):
        return self._elements.copy()

    def elements_properties(self):
        return {e.Name: e.properties() for e in self._elements}

    def finalize(self):
        self.interrupt(dispose=True)
        self.__bus.disconnect_by_func(self.__on_message)

        for element in self._elements:
            element.dispose()

    def input_uri(self):
        try:
            return self._elements[0].input_uri()
        except Exception:
            pass

    def interrupt(self, dispose=False, emit=True):
        for element in self._elements:
            element.interrupt()

        self._gst_pipe.set_state(Gst.State.NULL)
        if dispose:
            self.state = MediaState.Null
        else:
            self._gst_pipe.set_state(Gst.State.READY)
            self.state = MediaState.Stopped

        self._loop_count = self.__loop

        if emit:
            self.interrupted.emit(self)

    def properties(self):
        properties = super().properties().copy()
        properties['elements'] = self.elements_properties()
        return properties

    def update_elements(self, properties):
        for element in self._elements:
            if element.Name in properties:
                element.update_properties(properties[element.Name])

    def update_properties(self, properties):
        elements_properties = properties.pop('elements', {})
        super().update_properties(properties)

        self.update_elements(elements_properties)

        if self.state == MediaState.Null or self.state == MediaState.Error:
            self.state = MediaState.Stopped

    def _pipe_elements(self):
        tmp = {}
        tmp.update(elements.inputs())
        tmp.update(elements.outputs())
        tmp.update(elements.plugins())
        return tmp

    def __uri_changed(self, value):
        # Save the current mtime (file flag for last-change time)
        mtime = self._mtime
        # If the uri is a file, then update the current mtime
        if value.split('://')[0] == 'file':
            self._mtime = path.getmtime(value.split('//')[1])

        # If something is changed or the duration is invalid
        if mtime != self._mtime or self.duration < 0:
            self.__duration()

    def __append_element(self, element):
        if len(self._elements) > 0:
            self._elements[-1].link(element)

        self._elements.append(element)

    def __remove_element(self, index):
        if index > 0:
            self._elements[index - 1].unlink(self._elements[index])
        if index < len(self._elements) - 1:
            self._elements[index - 1].link(self._elements[index + 1])
            self._elements[index].unlink(self._elements[index])

        self._elements.pop(index).finalize()

    def __build_pipeline(self):
        # Set to NULL the pipeline
        if self._gst_pipe is not None:
            self.interrupt(dispose=True)
        # Remove all pipeline children
        for __ in range(self._gst_pipe.get_children_count()):
            self._gst_pipe.remove(self._gst_pipe.get_child_by_index(0))
        # Remove all the elements
        for __ in range(len(self._elements)):
            self.__remove_element(len(self._elements) - 1)

        # Create all the new elements
        elements = self._pipe_elements()
        for element in self.pipe.split('!'):
            self.__append_element(elements[element](self._gst_pipe))

        # Set to Stopped/READY the pipeline
        self.state = MediaState.Stopped
        self._gst_pipe.set_state(Gst.State.READY)

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
            self.interrupt(dispose=True, emit=False)
            self.error.emit(self, str(err), str(debug))

    def __on_eos(self):
        self.state = MediaState.Stopped
        self.eos.emit(self)

        if self._loop_count > 0 or self.loop == -1:
            self._gst_pipe.set_state(Gst.State.READY)

            self._loop_count -= 1
            self.play()
        else:
            self.interrupt()

    @async_in_pool(pool=ThreadPoolExecutor(cpu_count()))
    def __duration(self):
        self.duration = gst_uri_duration(self.input_uri())
