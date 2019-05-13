# This file is part of Linux Show Player
#
# Copyright 2017 Francesco Ceruti <ceppofrancy@gmail.com>
# Copyright 2016-2017 Thomas Achtner <info@offtools.de>
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
from enum import Enum
from threading import Lock

from lisp.core.clock import Clock
from lisp.core.signal import Connection
from lisp.cues.cue_time import CueTime
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)


class TcFormat(Enum):
    FILM = 1000 / 24
    EBU = 1000 / 25
    SMPTE = 1000 / 30


class HRCueTime(CueTime):
    _Clock = Clock(30)  # 1000 / 30  = 33.3333 milliseconds


class TimecodeCueTracker:
    def __init__(self, protocol, tc_format):
        """
        :param protocol: The protocol to be use to send timecode
        :type protocol: lisp.plugins.timecode.protocol.TimecodeProtocol
        :param tc_format: The format in which to send timecode
        :type tc_format: TcFormat
        """

        self.format = tc_format
        self.__protocol = protocol

        self.__cue = None
        self.__cue_time = None

        self.__track = 0
        self.__replace_hours = False

        self.__lock = Lock()

    @property
    def cue(self):
        """
        :rtype: lisp.cues.cue.Cue
        """
        return self.__cue

    @property
    def protocol(self):
        """
        :rtype: lisp.plugins.timecode.protocol.TimecodeProtocol
        """
        return self.__protocol

    @protocol.setter
    def protocol(self, protocol):
        """
        :type protocol: lisp.plugins.timecode.protocol.TimecodeProtocol
        """
        with self.__lock:
            self.__protocol.finalize()
            self.__protocol = protocol

    def track(self, cue):
        """Start tracking a new cue, untrack the current, if any"""

        if cue is self.__cue:
            return

        # Stop tracking
        self.untrack()

        # Setup new cue and options
        self.__cue = cue
        self.__cue_time = HRCueTime(cue)
        self.__replace_hours = cue.timecode["replace_hours"]
        self.__track = cue.timecode["track"] if self.__replace_hours else -1

        # Send a "starting" time
        self.send(self.__cue.current_time())
        # Start watching the new cue
        self.__cue_time.notify.connect(self.send, Connection.QtQueued)

    def untrack(self):
        """Stop tracking the current cue"""
        with self.__lock:
            if self.__cue is not None:
                self.__cue_time.notify.disconnect(self.send)

                self.__cue_time = None
                self.__cue = None

    def send(self, time):
        """Send time as timecode"""
        if self.__lock.acquire(blocking=False):
            try:
                if not self.__protocol.send(self.format, time, self.__track):
                    logger.warning(
                        translate(
                            "TimecodeWarning",
                            "Cannot send timecode, untracking cue",
                        )
                    )
                    self.untrack()
            except Exception:
                self.__lock.release()

    def finalize(self):
        self.untrack()
        self.protocol = None
