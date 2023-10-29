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

import logging
from abc import ABC, abstractmethod

from mido import Message

from lisp.core.signal import Signal
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)


class MIDIBase(ABC):
    def __init__(self, backend, port_name=None):
        """
        :param port_name: the port name
        """
        self._backend = backend
        self._port_name = port_name
        self._port = None

    @property
    def backend(self):
        return self._backend

    @property
    def port(self):
        return self._port

    def port_name(self, real=True):
        if real and self._port is not None:
            return self._port.name
        else:
            return self._port_name

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
            self._port = None

    def is_open(self):
        if self._port is not None:
            return not self._port.closed

        return False


class MIDIOutput(MIDIBase):
    def send(self, message):
        if self._port is not None:
            self._port.send(message)

    def open(self):
        try:
            self._port = self._backend.open_output(self._port_name)
        except OSError:
            logger.exception(
                translate(
                    "MIDIError", "Cannot connect to MIDI output port '{}'."
                ).format(self._port_name)
            )


class MIDIInput(MIDIBase):
    def __init__(self, *args):
        super().__init__(*args)

        self.alternate_mode = False
        self.new_message = Signal()
        self.new_message_alt = Signal()

    def open(self):
        try:
            self._port = self._backend.open_input(
                name=self._port_name, callback=self.__new_message
            )
        except OSError:
            logger.exception(
                translate(
                    "MIDIError", "Cannot connect to MIDI input port '{}'."
                ).format(self._port_name)
            )

    def __new_message(self, message):
        # Translate "Note On" with Velocity=0 to "Note Off"
        # See https://github.com/mido/mido/issues/130
        if message.type == "note_on" and message.velocity == 0:
            return Message.from_dict(
                {
                    **message.dict(),
                    "type": "note_off",
                }
            )

        if self.alternate_mode:
            self.new_message_alt.emit(message)
        else:
            self.new_message.emit(message)
