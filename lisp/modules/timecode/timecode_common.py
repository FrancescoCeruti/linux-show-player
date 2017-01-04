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
from abc import abstractmethod

from lisp.ui import elogging
from lisp.core.singleton import ABCSingleton
from lisp.core.configuration import config
from lisp.modules.timecode.backends import list_backends


class TcFormat(Enum):
    FILM = 1000 / 24
    EBU = 1000 / 25
    SMPTE = 1000 / 30


class TimecodeCommon(metaclass=ABCSingleton):
    def __init__(self):
        self._backend_name = config['Timecode']['backend']
        self._backend = None

    @abstractmethod
    def init(self):
        """set timecode backend"""

    def change_backend(self, bk_name):
        if bk_name in list_backends():
            self._backend_name = bk_name
            self.init()

    def status(self):
        """returns the status of the backend"""
        return config['Timecode'].getboolean('enabled') and self._backend and self._backend.status()

    def _disable(self):
        config.set('Timecode', 'enabled', 'False')
        self._backend = None
        elogging.error('TIMECODE: backend {0} not available, timecode disabled!'.format(self._backend_name))