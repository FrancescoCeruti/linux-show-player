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

from lisp.modules.midi.midi_common import MIDICommon


class MIDIOutputProvider(QObject, MIDICommon):
    # Only when not in alternate-mode
    new_message = pyqtSignal(mido.messages.BaseMessage)
    # Only when in alternate-mode
    new_message_alt = pyqtSignal(mido.messages.BaseMessage)

    def __init__(self, port_name='default', backend_name=None):
        super().__init__()

    def send(self, type_, **kwargs):
        self.__port.send(mido.Message(type_, **kwargs))

    def __open_port(self):
        # I don't expect to find a __port named "default", if so, I assume
        # this __port is the default one.
        if self.__port_name in self.get_input_names():
            self.__port = self.__backend.open_output(self.__port_name)
        else:
            # If the __port isn't available use the default one
            self.__port = self.__backend.open_output()