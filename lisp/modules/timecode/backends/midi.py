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

from lisp.modules.timecode.timecode_backend import TimecodeBackend
from lisp.modules.timecode.timecode_common import TcFormat


class Midi(TimecodeBackend):
    Name = 'MIDI'

    __format__ = {TcFormat.FILM: 0,
                  TcFormat.EBU: 1,
                  TcFormat.SMPTE: 3}

    def __init__(self):
        """this backend uses the midi module"""
        super().__init__()

    def send(self, format, hours, minutes, seconds, frames, rewind=False):
        return False