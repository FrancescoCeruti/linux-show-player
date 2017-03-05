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

from enum import Enum

from lisp.core.clock import Clock
from lisp.core.configuration import config
from lisp.core.signal import Connection
from lisp.core.singleton import ABCSingleton
from lisp.cues.cue_time import CueTime
from lisp.plugins.timecode import protocols
from lisp.ui import elogging


class TcFormat(Enum):

    FILM = 1000 / 24
    EBU = 1000 / 25
    SMPTE = 1000 / 30
    

class HRCueTime(CueTime):
    _Clock = Clock(30)  # 1000 /30  = 33.3333 milliseconds


class TimecodeCommon(metaclass=ABCSingleton):
    def __init__(self):
        self.__protocol_name = config['Timecode']['protocol']
        self.__protocol = None

        self.__cue = None
        self.__cue_time = None

        self.__track = 0
        self.__format = TcFormat[config['Timecode']['format']]
        self.__replace_hours = False

        # load timecode protocol components
        protocols.load_protocols()

    @property
    def cue(self):
        """current cue, which timecode is send"""
        return self.__cue

    @property
    def status(self):
        """returns the status of the protocol"""
        return self.__protocol and self.__protocol.status()

    @property
    def protocol(self):
        return self.__protocol.Name

    def init(self):
        """set timecode protocol"""
        self.__protocol = protocols.get_protocol(self.__protocol_name)

        if self.__protocol.status():
            elogging.debug("TIMECODE: protocol created - {0}".format(self.__protocol.Name))
        else:
            elogging.error("TIMECODE: error creating protocol - {0}".format(self.__protocol.Name), dialog=False)

    def change_protocol(self, protocol_name):
        if protocol_name in protocols.list_protocols():
            self.__protocol_name = protocol_name
            self.init()

    def start(self, cue):
        """initialize timecode for new cue, stop old"""
        if not self.status:
            return

        # Stop the currently "running" timecode
        self.stop(rcue=self.__cue)

        # Reload format settings
        self.__format = TcFormat[config['Timecode']['format']]

        # Setup new cue and options
        self.__cue = cue
        self.__cue_time = HRCueTime(cue)
        self.__replace_hours = cue.timecode['replace_hours']
        if self.__replace_hours:
            self.__track = cue.timecode['track']
        else:
            self.__track = -1

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

        if self.status:
            self.__protocol.stop(rclient)

    def send(self, time):
        """sends timecode"""
        if not self.__protocol.send(self.__format, time, self.__track):
            elogging.error('TIMECODE: could not send timecode, stopping timecode', dialog=False)
            self.stop()
