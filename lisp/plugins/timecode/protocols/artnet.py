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


from ola.OlaClient import OlaClient, OLADNotRunningException

from lisp.ui.ui_utils import translate
from lisp.core.util import time_tuple
from lisp.plugins.timecode.timecode_common import TcFormat
from lisp.plugins.timecode.timecode_protocol import TimecodeProtocol
from lisp.ui import elogging


class Artnet(TimecodeProtocol):
    Name = 'ArtNet'

    __format__ = {TcFormat.FILM: OlaClient.TIMECODE_FILM,
                  TcFormat.EBU: OlaClient.TIMECODE_EBU,
                  TcFormat.SMPTE: OlaClient.TIMECODE_SMPTE}

    def __init__(self):
        super().__init__()
        try:
            self.__client = OlaClient()
        except OLADNotRunningException as e:
            self.__client = None
            elogging.error(translate('TIMECODE: Could not create OlaClient'),
                           details="{0}".format(e), dialog=False)

        self.__last_time = -1

    def status(self):
        return bool(self.__client)

    def send(self, fmt, time, track=-1):
        if self.__last_time + fmt.value >= time:
            return

        tt = time_tuple(time)

        hours = tt[0]
        if track > -1:
            hours = track
        minutes = tt[1]
        seconds = tt[2]
        frames = int(tt[3] / fmt.value)

        try:
            self.__client.SendTimeCode(self.__format__[fmt],
                                       hours,
                                       minutes,
                                       seconds,
                                       frames)

        except OLADNotRunningException:
            elogging.error(
                translate('Timecode', 'Cannot send timecode.'),
                details=translate('Timecode', 'OLA has stopped.'))
            return False
        except Exception as e:
            elogging.exception('Cannot send timecode.', e, dialog=False)
            return False

        self.__last_time = time
        return True

    def stop(self, rclient=False):
        self.__last_time = -1

        if rclient:
            self.__client = None
