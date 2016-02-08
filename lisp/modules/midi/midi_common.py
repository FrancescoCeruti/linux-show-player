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
from abc import abstractmethod

import mido

from lisp.core.singleton import QSingleton


class MIDICommon(metaclass=QSingleton):
    def __init__(self, port_name='default', backend_name=None):
        super().__init__()

        self.__backend_name = backend_name
        self.__port_name = port_name
        self.__backend = None
        self.__port = None

    def start(self):
        if self.__backend is None:
            try:
                self.__backend = mido.Backend(self.__backend_name, load=True)
                self.__open_port()
            except Exception:
                raise RuntimeError(
                    'Backend loading failed: ' + self.__backend_name)

    def stop(self):
        self.__close_port()
        self.__backend = None

    def change_backend(self, backend_name):
        self.stop()
        self.__backend_name = backend_name
        self.start()

    def change_port(self, port_name):
        self.__port_name = port_name
        self.__close_port()
        self.__open_port()

    def get_input_names(self):
        if self.__backend is not None:
            return self.__backend.get_input_names()

        return []

    @abstractmethod
    def __open_port(self):
        """
            Open the port
        """

    def __close_port(self):
        if self.__port is not None:
            self.__port.close()