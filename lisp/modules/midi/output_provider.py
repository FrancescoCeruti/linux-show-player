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

import mido

from lisp.modules.midi.midi_common import MIDICommon


class MIDIOutputProvider(MIDICommon):

    def __init__(self, port_name='default', backend_name=None):
        super().__init__(port_name=port_name, backend_name=backend_name)

    def send(self, type_, **kwargs):
        self._port.send(mido.Message(type_, **kwargs))

    def _open_port(self):
        # I don't expect to find a port named "default", if so, I assume
        # this port is the default one.
        if self._port_name in self.get_input_names():
            self._port = self._backend.open_output(self._port_name)
        else:
            # If the port isn't available use the default one
            self._port = self._backend.open_output()