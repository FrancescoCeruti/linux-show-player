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

from ola.OlaClient import OlaClient
from lisp.modules.timecode.timecode_backend import TimecodeBackend
from lisp.modules.timecode.timecode_common import TcFormat


class Artnet(TimecodeBackend):
    Name = 'ArtNet'

    __format__ = {TcFormat.FILM: OlaClient.TIMECODE_FILM,
                  TcFormat.EBU: OlaClient.TIMECODE_EBU,
                  TcFormat.SMPTE: OlaClient.TIMECODE_SMPTE}

    def __init__(self):
        super().__init__()
        self.__client = OlaClient()

    def send(self, format, hours, minutes, seconds, frames, rewind=False):
        try:
            self.__client.SendTimeCode(self.__format__[format],
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

        return True

    def stop(self, rclient=False):
        if rclient:
            self.__client = None