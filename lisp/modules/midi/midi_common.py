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

from lisp.core.singleton import ABCSingleton


class MIDICommon(metaclass=ABCSingleton):

    def __init__(self, port_name='AppDefault'):
        """
        :param port_name: the port name

        The port name can be:
            * SysDefault  - the system default port
            * AppDefault  - the app default port defined in the config file
            * <port_name> - the port name
        """
        self._bakend = None
        self._port_name = port_name
        self._port = None

    def change_port(self, port_name):
        self._port_name = port_name
        self.close()
        self.open()

    @abstractmethod
    def open(self):
        """Open the port"""

    def close(self):
        """Close the port"""
        if self._port is not None:
            self._port.close()

    def is_open(self):
        if self._port is not None:
            return not self._port.closed

        return False
