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

from ola.OlaClient import OlaClient, OLADNotRunningException

from lisp.core.util import time_tuple
from lisp.plugins.timecode.cue_tracker import TcFormat
from lisp.plugins.timecode.protocol import TimecodeProtocol
from lisp.ui.ui_utils import translate

ARTNET_FORMATS = {
    TcFormat.FILM: OlaClient.TIMECODE_FILM,
    TcFormat.EBU: OlaClient.TIMECODE_EBU,
    TcFormat.SMPTE: OlaClient.TIMECODE_SMPTE,
}

logger = logging.getLogger(__name__)


class Artnet(TimecodeProtocol):
    Name = "ArtNet"

    def __init__(self):
        super().__init__()

        try:
            self.__client = OlaClient()
        except OLADNotRunningException as e:
            raise e

        self.__last_time = -1

    def send(self, fmt, time, track=-1):
        if self.__last_time + fmt.value >= time:
            return

        hours, minutes, seconds, millis = time_tuple(time)
        frame = int(millis / fmt.value)
        if track > -1:
            hours = track

        try:
            self.__client.SendTimeCode(
                ARTNET_FORMATS[fmt], hours, minutes, seconds, frame
            )
        except OLADNotRunningException:
            logger.error(
                translate(
                    "TimecodeError",
                    "Cannot send timecode. \nOLA daemon has stopped.",
                )
            )
            return False
        except Exception:
            logger.exception(
                translate("TimecodeError", "Cannot send timecode.")
            )
            return False

        self.__last_time = time
        return True

    def finalize(self):
        self.__last_time = -1
        self.__client = None
