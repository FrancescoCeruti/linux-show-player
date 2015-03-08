##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from os import cpu_count as ocpu_count
from os.path import getmtime
from re import match
from threading import Lock

from lisp.repository import Gst
from lisp.core.media import Media
from lisp.gst import elements
from lisp.utils import audio_utils

from lisp.utils.decorators import async, synchronized
from lisp.utils.util import deep_update


def cpu_count():
    return ocpu_count() if ocpu_count() is not None else 1


class GstMedia(Media):

    def __init__(self, properties={}, **kwds):
        super().__init__(**kwds)

        self._elements = []
        self._properties = {}
        self._gst_pipe = Gst.Pipeline()
        self._gst_state = Gst.State.NULL
        self._loop_count = 0

        self.__pipe = ''
        self.__do_seek = False
        self.__stop_pause_lock = Lock()

        self.__bus = self._gst_pipe.get_bus()
        self.__bus.add_signal_watch()
        self.__bus.connect('message', self.__on_message)

        default = {'duration': -1, 'mtime': -1, 'loop': 0, 'start_at': 0,
                   'pipe': ''}
        self.update_properties(default)
        self.update_properties(properties)

    def current_time(self):
        if(self._gst_state == Gst.State.PLAYING or
           self._gst_state == Gst.State.PAUSED):
            return (self._gst_pipe.query_position(Gst.Format.TIME)[1] //
                    Gst.MSECOND)
        else:
            return -1

    @async
    @synchronized(blocking=False)
    def play(self, emit=True):
        if self.state == Media.STOPPED or self.state == Media.PAUSED:
            if emit:
                self.on_play.emit(self)

            self.__play(emit)

    def __play(self, emit, seek_mode=False):
        self._gst_pipe.set_state(Gst.State.PLAYING)
        self._gst_pipe.get_state(1 * Gst.SECOND)

        self.state = Media.PLAYING
        if not seek_mode and self['start_at'] > 0:
            self.seek(self['start_at'], emit=False)

        if emit:
            self.played.emit(self)

    @async
    @synchronized(blocking=False)
    def pause(self, emit=True):
        if self.state == Media.PLAYING:
            if emit:
                self.on_pause.emit(self)

            for element in self._elements:
                element.pause()

            self.state = Media.PAUSED
            self._gst_pipe.set_state(Gst.State.PAUSED)
            if emit:
                self.paused.emit(self)

    @async
    @synchronized(blocking=False)
    def stop(self, emit=True):
        if self.state == Media.PLAYING or self.state == Media.PAUSED:
            if emit:
                self.on_stop.emit(self)

            for element in self._elements:
                element.stop()

            self.interrupt(emit=False)
            if emit:
                self.stopped.emit(self)

    def seek(self, position, emit=True):
        # If state is NONE the track cannot be sought
        if self.state != self.NONE:
            if position < self['duration']:
                if self.state == self.STOPPED:
                    if emit:
                        self.on_play.emit(self)

                    self.__play(emit, seek_mode=True)

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
                if emit:
                    self.sought.emit(self, position)

    def element(self, name):
        for element in self._elements:
            if element.Name == name:
                return element

    def elements(self):
        return self._elements.copy()

    def elements_properties(self):
        properties = {}

        for element in self._elements:
            properties[element.Name] = element.properties()

        return properties

    def dispose(self):
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
            self.state = Media.NONE
        else:
            self._gst_pipe.set_state(Gst.State.READY)
            self.state = Media.STOPPED

        self._loop_count = self['loop']

        if emit:
            self.interrupted.emit(self)

    def properties(self):
        properties = self._properties.copy()
        properties['elements'] = self.elements_properties()
        return properties

    def update_elements(self, conf, emit=True):
        old_uri = self.input_uri()

        if 'elements' not in self._properties:
            self['elements'] = {}
        for element in self._elements:
            if element.Name in conf:
                element.update_properties(conf[element.Name])
                self['elements'][element.Name] = element.properties()

        uri = self.input_uri()
        if uri is not None:
            # Save the current mtime (file flag for last-change time)
            mtime = self['mtime']
            # If the uri is a file, then update the current mtime
            if uri.split('://')[0] == 'file':
                self['mtime'] = getmtime(uri.split('//')[1])

            # If something is changed or the duration is invalid
            if old_uri != uri or mtime != self['mtime'] or self['duration'] < 0:
                self.__duration()
        else:
            # If no URI is provided, set and emit a 0 duration
            self['duration'] = 0
            self.duration.emit(self, 0)

        if emit:
            self.media_updated.emit(self)

    def update_properties(self, properties, emit=True):
        elements = properties.pop('elements', {})
        deep_update(self._properties, properties)

        self['pipe'] = self['pipe'].replace(' ', '')
        self._loop_count = self['loop']

        if self.__pipe != self['pipe']:
            self.__validate_pipe()
            self.__build_pipeline()
            self.__pipe = self['pipe']

        self.update_elements(elements, False)

        if self.state == self.NONE:
            self.state = self.STOPPED

        if emit:
            self.media_updated.emit(self)

    def _pipe_regex(self):
        return ('^(' + '!|'.join(elements.inputs().keys()) + '!)'
                '(' + '!|'.join(elements.plugins().keys()) + '!)*'
                '(' + '|'.join(elements.outputs().keys()) + ')$')

    def _pipe_elements(self):
        tmp = {}
        tmp.update(elements.inputs())
        tmp.update(elements.outputs())
        tmp.update(elements.plugins())
        return tmp

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

        self._elements.pop(index).dispose()

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
        for element in self['pipe'].split('!'):
            self.__append_element(elements[element](self._gst_pipe))

        # Set to STOPPED/READY the pipeline
        self.state = Media.STOPPED
        self._gst_pipe.set_state(Gst.State.READY)

    def __validate_pipe(self):
        if match(self._pipe_regex(), self['pipe']) is None:
            raise Exception('Wrong pipeline syntax!')

        # Remove duplicates
        self['pipe'] = '!'.join(OrderedDict.fromkeys(self['pipe'].split('!')))

    def __on_message(self, bus, message):
        if message.src == self._gst_pipe:
            if message.type == Gst.MessageType.STATE_CHANGED:
                self._gst_state = message.parse_state_changed()[1]

                '''if self._gst_state == Gst.State.PLAYING and self.__do_seek:
                    self.seek(self.__do_seek)
                    self.__do_seek = False'''
            elif message.type == Gst.MessageType.EOS:
                self.__on_eos()
            elif message.type == Gst.MessageType.CLOCK_LOST:
                self._gst_pipe.set_state(Gst.State.PAUSED)
                self._gst_pipe.set_state(Gst.State.PLAYING)

        if message.type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            # print('Error: ' + str(err) + '\n' + str(debug))

            self.interrupt(dispose=True, emit=False)
            self.error.emit(self, str(err), str(debug))

    def __on_eos(self):
        self.state = Media.STOPPED
        self.eos.emit(self)

        if self._loop_count > 0 or self['loop'] == -1:
            self._gst_pipe.set_state(Gst.State.READY)

            self._loop_count -= 1
            self.play()
        else:
            self.interrupt()

    @async(pool=ThreadPoolExecutor(cpu_count()))
    def __duration(self):
        self['duration'] = int(audio_utils.uri_duration(self.input_uri()))
        self.duration.emit(self, self['duration'])

    def __setitem__(self, key, value):
        self._properties[key] = value
