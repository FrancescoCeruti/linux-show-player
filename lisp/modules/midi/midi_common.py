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

from lisp.core.singleton import Singleton


class MIDICommon(metaclass=Singleton):
    def __init__(self, port_name='default', backend_name=None):
        super().__init__()

        self._backend_name = backend_name
        self._port_name = port_name
        self._backend = None
        self._port = None

    def start(self):
        if self._backend is None:
            try:
                self._backend = mido.Backend(self._backend_name, load=True)
                self._open_port()
            except Exception:
                raise RuntimeError(
                    'Backend loading failed: ' + self._backend_name)

    def stop(self):
        self._close_port()
        self._backend = None

    def change_backend(self, backend_name):
        self.stop()
        self._backend_name = backend_name
        self.start()

    def change_port(self, port_name):
        self._port_name = port_name
        self._close_port()
        self._open_port()

    def get_input_names(self):
        if self._backend is not None:
            return self._backend.get_input_names()

        return []

    @abstractmethod
    def _open_port(self):
        """
            Open the port
        """

    def _close_port(self):
        if self._port is not None:
            self._port.close()