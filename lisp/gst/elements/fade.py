##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from threading import Lock
from time import sleep

from PyQt5 import QtCore
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

from lisp.gst.gst_element import GstMediaElement
from lisp.utils.decorators import async
from lisp.utils.fade_functor import *


class Fade(QtCore.QObject, GstMediaElement):

    Type = GstMediaElement.TYPE_PLUGIN
    Name = 'Fade'

    # Fade in/out signals
    enter_fadein = QtCore.pyqtSignal()
    exit_fadein = QtCore.pyqtSignal()
    enter_fadeout = QtCore.pyqtSignal()
    exit_fadeout = QtCore.pyqtSignal()

    # Fade functors
    FadeIn = {'Linear': fade_linear,
              'Quadratic': fadein_quad,
              'Quadratic2': fade_inout_quad}
    FadeOut = {'Linear': fade_linear,
               'Quadratic': fadeout_quad,
               'Quadratic2': fade_inout_quad}

    def __init__(self, pipe):
        super().__init__()

        self._properties = {'fadein': .0,
                            'fadein_type': 'Linear',
                            'fadeout': .0,
                            'fadeout_type': 'Linear'
                            }

        # Mutual exclusion
        self._lock = Lock()
        '''
            This flag is needed because when a fadeout occurs during a fadein,
            or vice versa, the current fade must end before the new starts.
            The _fadein method set the flag at True, and could run until the
            flag value is True, same for the _fadeout method but with the flag
            set to False.
        '''
        self._flag = False
        # A fade function could run until the Pipeline is playing
        self._playing = False

        self._volume = Gst.ElementFactory.make('volume', None)
        pipe.add(self._volume)

        self._convert = Gst.ElementFactory.make('audioconvert', None)
        pipe.add(self._convert)

        self._volume.link(self._convert)

        self._bus = pipe.get_bus()
        self._bus.add_signal_watch()
        self._handler = self._bus.connect('message', self._on_message)

    def properties(self):
        return self._properties

    def set_property(self, name, value):
        if name in self._properties:
            self._properties[name] = value

        if name == 'fadein' and not self._playing:
            if value > 0:
                self._volume.set_property('volume', 0)
            else:
                self._volume.set_property('volume', 1)

    def stop(self):
        if self._properties['fadeout'] > 0:
            self._flag = False

            self._fadeout()

    pause = stop

    def dispose(self):
        self._bus.remove_signal_watch()
        self._bus.disconnect(self._handler)

    @async
    def _fadein(self):
        self._flag = True
        self._lock.acquire()

        try:
            self.enter_fadein.emit()

            functor = self.FadeIn[self._properties['fadein_type']]
            duration = self._properties['fadein'] * 100
            volume = self._volume.get_property('volume')
            time = 0

            while time <= duration and self._flag and self._playing:
                self._volume.set_property('volume',
                                          functor(ntime(time, 0, duration),
                                                  1 - volume, volume))
                time += 1
                sleep(0.01)

            self.exit_fadein.emit()
        finally:
            self._lock.release()

    def _fadeout(self):
        self._flag = False
        self._lock.acquire()

        try:
            self.enter_fadeout.emit()

            functor = self.FadeOut[self._properties['fadeout_type']]
            duration = self._properties['fadeout'] * 100
            volume = self._volume.get_property('volume')
            time = 0

            while time <= duration and not self._flag and self._playing:
                self._volume.set_property('volume',
                                          functor(ntime(time, 0, duration),
                                                  -volume, volume))
                time += 1
                sleep(0.01)

            self.exit_fadeout.emit()
        finally:
            self._lock.release()

    def _on_message(self, bus, message):
        if message.src == self._volume:
            if message.type == Gst.MessageType.STATE_CHANGED:
                state = message.parse_state_changed()[1]

                self._playing = state == Gst.State.PLAYING

                if self._properties['fadein'] > 0:
                    # If gone in PLAYING state then start the fadein
                    if self._playing:
                        self._fadein()
                    else:
                        # The next time the volume must start from 0
                        self._volume.set_property('volume', 0)
                elif not self._playing:
                    self._volume.set_property('volume', 1)

    def sink(self):
        return self._volume

    def src(self):
        return self._convert
