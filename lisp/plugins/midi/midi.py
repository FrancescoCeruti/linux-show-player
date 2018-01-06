# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2017 Francesco Ceruti <ceppofrancy@gmail.com>
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

from lisp.core.plugin import Plugin
from lisp.plugins.midi.midi_input import MIDIInput
from lisp.plugins.midi.midi_output import MIDIOutput
from lisp.plugins.midi.midi_settings import MIDISettings
from lisp.ui.settings.app_settings import AppSettings


class Midi(Plugin):
    """Provide MIDI I/O functionality"""

    Name = 'MIDI'
    Authors = ('Francesco Ceruti', )
    Description = 'Provide MIDI I/O functionality'

    def __init__(self, app):
        super().__init__(app)

        # Register the settings widget
        AppSettings.register_settings_widget(MIDISettings, Midi.Config)

        # Load the backend and set it as current mido backend
        self.backend = mido.Backend(Midi.Config['Backend'], load=True)
        mido.set_backend(self.backend)

        # Create default I/O and open the ports/devices
        self.__input = MIDIInput(
            self._input_name(Midi.Config['InputDevice']))
        self.__input.open()

        self.__output = MIDIOutput(
            self._output_name(Midi.Config['OutputDevice']))
        self.__output.open()

    def _input_name(self, port_name):
        """Check if port_name exists as an input port for the current backend.

        :param port_name: The input port name to check
        :type port_name: str

        :returns The input port name if exists, None otherwise
        """
        if port_name != "" and port_name in self.backend.get_input_names():
            return port_name

    def _output_name(self, port_name):
        """Check if port_name exists as an output port for the current backend.

        :param port_name: The output port name to check
        :type port_name: str

        :returns The output port name if exists, None otherwise
        """
        if port_name != "" and port_name in self.backend.get_output_names():
            return port_name

    @property
    def input(self):
        return self.__input

    @property
    def output(self):
        return self.__output
