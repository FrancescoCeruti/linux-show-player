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

from lisp.core.singleton import ABCSingleton
from lisp.core.configuration import config
from lisp.modules.timecode import backends


class TcFormat(Enum):
    FILM = 1000 / 24
    EBU = 1000 / 25
    SMPTE = 1000 / 30


class TimecodeCommon(metaclass=ABCSingleton):
    def __init__(self):
        bk_name = config['Timecode']['backend']
        self.__backend = backends.get(bk_name)
        print("self.__backend ", self.__backend)

    def __get_backend(self):
        return self.__backend

    def __set_backend(self, backend_name):
        if backend_name in backends.list():
            self.__backend = backends.get(backends)
        else:
            raise Exception('Could not create Timecode Backend: {}'.format(backend_name))

    backend = property(__get_backend, __set_backend)