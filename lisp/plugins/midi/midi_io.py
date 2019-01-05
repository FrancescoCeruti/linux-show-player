# This file is part of Linux Show Player
#
# Copyright 2019 Francesco Ceruti <ceppofrancy@gmail.com>
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
from abc import ABC, abstractmethod

from lisp.core.signal import Signal
from lisp.plugins.midi.midi_utils import mido_backend


class MIDIBase(ABC):
    def __init__(self, port_name=None):
        """
        :param port_name: the port name
        """
        self._backend = None
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


class MIDIOutput(MIDIBase):
    def __init__(self, port_name=None):
        super().__init__(port_name=port_name)

    def send_from_str(self, str_message):
        self.send(mido.parse_string(str_message))

    def send(self, message):
        self._port.send(message)

    def open(self):
        self._port = mido_backend().open_output(self._port_name)


class MIDIInput(MIDIBase):
    def __init__(self, port_name=None):
        super().__init__(port_name=port_name)

        self.alternate_mode = False
        self.new_message = Signal()
        self.new_message_alt = Signal()

    def open(self):
        self._port = mido_backend().open_input(
            name=self._port_name, callback=self.__new_message
        )

    def __new_message(self, message):
        if self.alternate_mode:
            self.new_message_alt.emit(message)
        else:
            self.new_message.emit(message)
