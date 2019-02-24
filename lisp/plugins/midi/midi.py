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
from PyQt5.QtCore import QT_TRANSLATE_NOOP

from lisp.core.plugin import Plugin
from lisp.cues.cue_factory import CueFactory
from lisp.plugins.midi.midi_cue import MidiCue
from lisp.plugins.midi.midi_io import MIDIOutput, MIDIInput
from lisp.plugins.midi.midi_settings import MIDISettings
from lisp.ui.settings.app_configuration import AppConfigurationDialog


class Midi(Plugin):
    """Provide MIDI I/O functionality"""

    Name = "MIDI"
    Authors = ("Francesco Ceruti",)
    Description = "Provide MIDI I/O functionality"

    def __init__(self, app):
        super().__init__(app)

        # Register the settings widget
        AppConfigurationDialog.registerSettingsPage(
            "plugins.midi", MIDISettings, Midi.Config
        )
        # Register cue
        CueFactory.register_factory(MidiCue.__name__, MidiCue)
        app.window.registerSimpleCueMenu(
            MidiCue, QT_TRANSLATE_NOOP("CueCategory", "Integration cues")
        )

        # Load the backend and set it as current mido backend
        self.backend = mido.Backend(Midi.Config["backend"], load=True)
        mido.set_backend(self.backend)

        # Create default I/O and open the ports/devices
        self.__input = MIDIInput(self._input_name(Midi.Config["inputDevice"]))
        self.__input.open()

        self.__output = MIDIOutput(
            self._output_name(Midi.Config["outputDevice"])
        )
        self.__output.open()

        Midi.Config.changed.connect(self.__config_change)
        Midi.Config.updated.connect(self.__config_update)

    def __config_change(self, key, value):
        if key == "inputDevice":
            self.__input.change_port(self._input_name(value))
        elif key == "outputDevice":
            self.__output.change_port(self._output_name(value))

    def __config_update(self, diff):
        for key, value in diff.items():
            self.__config_change(key, value)

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
