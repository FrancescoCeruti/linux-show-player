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
from PyQt5.QtCore import pyqtSignal, QObject

from lisp.core.signal import Signal
from lisp.modules.midi.midi_common import MIDICommon


class MIDIInputHandler(MIDICommon):

    def __init__(self, port_name='default', backend_name=None):
        super().__init__()

        self.alternate_mode = False
        self.new_message = Signal()
        self.new_message_alt = Signal()

    def __new_message(self, message):
        if self.alternate_mode:
            self.new_message_alt.emit(message)
        else:
            self.new_message.emit(message)

    def _open_port(self):
        # We don't expect to find a port named "default", if so, we assume
        # this port is the default one.
        if self._port_name in self.get_input_names():
            self._port = self._backend.open_input(self._port_name,
                                                  callback=self.__new_message)
        else:
            # If the port isn't available use the default one
            self._port = self._backend.open_input(callback=self.__new_message)
