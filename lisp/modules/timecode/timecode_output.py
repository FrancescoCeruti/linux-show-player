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

from lisp.core.configuration import config
from lisp.core.clock import Clock
from lisp.cues.cue_time import CueTime
from lisp.modules.timecode.timecode_common import TimecodeCommon, TcFormat


class HRCueTime(CueTime):
    _Clock = Clock(30)  # 1000 /30  = 33.3333 milliseconds


class TimecodeOutput(TimecodeCommon):
    def __init__(self):
        super().__init__()

        self.__cue = None
        self.__cue_time = None

        self.__track = 0
        self.__hres = config['Timecode'].getboolean('hres')
        self.__format = TcFormat[config['Timecode']['format']]
        self.__replace_hours = False
        self.__last_frame = -1

    @property
    def cue(self):
        return self.__cue

    def status(self):
        """returns the status of the backend"""
        return self.backend.status()

    def init(self, cue):
        """initialize timecode for new cue, stop old"""
        # Load cue settings, if enabled, otherwise return
        if not cue.timecode['enabled']:
            return

        # Stop the currently "running" timecode
        self.stop_timecode()

        # Reload format settings
        self.__hres = config['Timecode'].getboolean('hres')
        self.__format = TcFormat[config['Timecode']['format']]

        # Setup new cue and options
        self.__cue = cue
        self.__cue_time = HRCueTime(cue) if self.__hres else CueTime(cue)
        self.__replace_hours = cue.timecode['replace_hours']
        self.__track = cue.timecode['track']

    def start(self):
        """starts sending timecode of a new cue, send full frame"""
        self.send(self.__cue.current_time(), True)

        # Start watching the new cue
        self.__cue_time.notify.connect(
            self.send, Connection.QtQueued)

    def stop(self, rclient=False, rcue=False):
        """stops sending timecode"""
        if self.__cue_time is not None:
            self.__cue_time.notify.disconnect(self.send)

        self.__last_frame = -1

        if rcue:
            self.__cue = None
            self.__cue_time = None

        self.backend.stop(rclient)

    def send(self, time, rewind=False):
        """sends timecode"""
        tt = time_tuple(time)
        frame = int(tt[3] / self.__format.value)

        if self.__hres:
            if self.__last_frame == frame:
                return
            self.__last_frame = frame

        track = self.__track
        if not self.__replace_hours:
            track = tt[0]

        if not self.backend.send(self.__format, track, tt[1], tt[2], tt[3], rewind):
            # TODO: Error Handling
            raise RuntimeError('TODO')