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


class TimecodeBackend():
    """base class for timecode backends"""
    Name = 'None'

    def __init__(self):
        """constructor of timecode backend"""

    def status(self):
        """returns status of backend, True if ready"""
        return True

    def send(self, fmt, time, track=-1, rewind=False):
        """send timecode, returs success for error handling"""
        return False

    def stop(self, rclient=False):
        """cleanup after client has stopped"""
