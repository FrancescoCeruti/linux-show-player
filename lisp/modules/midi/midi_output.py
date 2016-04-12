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
from lisp.modules.midi.midi_utils import mido_backend, mido_port_name


class MIDIOutput(MIDICommon):
    def __init__(self, port_name='AppDefault'):
        super().__init__(port_name=port_name)

    def send_from_str(self, str_message):
        self.send(mido.parse_string(str_message))

    def send(self, message):
        self._port.send(message)

    def open(self):
        port_name = mido_port_name(self._port_name, 'O')
        self._port = mido_backend().open_output(port_name)
