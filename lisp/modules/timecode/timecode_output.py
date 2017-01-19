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

from lisp.core.signal import Connection
from lisp.ui import elogging
from lisp.core.configuration import config
from lisp.core.clock import Clock
from lisp.cues.cue_time import CueTime
from lisp.modules.timecode import backends
from lisp.modules.timecode.timecode_common import TimecodeCommon, TcFormat


class HRCueTime(CueTime):
    _Clock = Clock(30)  # 1000 /30  = 33.3333 milliseconds


class TimecodeOutput(TimecodeCommon):
    def __init__(self):
        super().__init__()

        self.__cue = None
        self.__cue_time = None

        self.__track = 0
        self.__format = TcFormat[config['Timecode']['format']]
        self.__replace_hours = False

    @property
    def cue(self):
        return self.__cue

    def init(self):
        self._backend = backends.create_backend(self._backend_name)
        if self._backend.status():
            elogging.debug("TIMECODE: backend created - {0}".format(self._backend.Name))
        else:
            self._disable()

    def start(self, cue):
        """initialize timecode for new cue, stop old"""
        if not cue.timecode['enabled'] or not self.status():
            return

        # Stop the currently "running" timecode
        self.stop(rcue=self.__cue)

        # Reload format settings
        self.__format = TcFormat[config['Timecode']['format']]

        # Setup new cue and options
        self.__cue = cue
        hres = config['Timecode'].getboolean('hres')
        self.__cue_time = HRCueTime(cue) if hres else CueTime(cue)
        self.__replace_hours = cue.timecode['replace_hours']
        self.__track = cue.timecode['track']

        self.send(self.__cue.current_time())

        # Start watching the new cue
        self.__cue_time.notify.connect(
            self.send, Connection.QtQueued)

    def stop(self, rclient=False, rcue=False):
        """stops sending timecode"""
        if self.__cue_time is not None:
            self.__cue_time.notify.disconnect(self.send)

        if rcue:
            self.__cue = None
            self.__cue_time = None

        if self.status():
            self._backend.stop(rclient)

    def send(self, time):
        """sends timecode"""
        if not self._backend.send(self.__format, time, self.__track):
            elogging.error('TIMECODE: could not send timecode, stopping timecode', dialog=False)
            self.stop()