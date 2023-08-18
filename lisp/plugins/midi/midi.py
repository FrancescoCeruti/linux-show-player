# This file is part of Linux Show Player
#
# Copyright 2023 Francesco Ceruti <ceppofrancy@gmail.com>
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

import mido
from PyQt5.QtCore import QT_TRANSLATE_NOOP

from lisp.core.plugin import Plugin
from lisp.core.signal import Connection
from lisp.plugins.midi.midi_cue import MidiCue
from lisp.plugins.midi.midi_io import MIDIOutput, MIDIInput, MIDIBase
from lisp.plugins.midi.midi_settings import MIDISettings
from lisp.plugins.midi.midi_utils import midi_output_names, midi_input_names
from lisp.plugins.midi.port_monitor import ALSAPortMonitor
from lisp.ui.settings.app_configuration import AppConfigurationDialog
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)


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
        app.cue_factory.register_factory(MidiCue.__name__, MidiCue)
        app.window.registerSimpleCueMenu(
            MidiCue, QT_TRANSLATE_NOOP("CueCategory", "Integration cues")
        )

        # Load the backend and set it as current mido backend
        self.backend = mido.Backend(Midi.Config["backend"], load=True)
        mido.set_backend(self.backend)

        # Define the default ports
        avail_inputs = self.backend.get_input_names()
        avail_outputs = self.backend.get_output_names()
        self.__default_input = avail_inputs[0] if avail_inputs else ""
        self.__default_output = avail_outputs[0] if avail_outputs else ""

        # Create input handlers and connect
        self.__inputs = []
        for name in self.input_names():
            self.__inputs.append(MIDIInput(self.backend, name))
            self._reconnect(self.__inputs[-1], name, avail_inputs)

        # Create output handlers and connect
        self.__outputs = []
        for name in self.output_names():
            self.__outputs.append(MIDIOutput(self.backend, name))
            self._reconnect(self.__outputs[-1], name, avail_outputs)

        # Monitor ports, for auto-reconnection.
        # Since current midi backends are not reliable on
        # connection/disconnection detection, we need to use the native APIs.
        self.port_monitor = ALSAPortMonitor()
        self.port_monitor.port_removed.connect(
            self._on_port_removed, Connection.QtQueued
        )
        self.port_monitor.port_added.connect(
            self._on_port_added, Connection.QtQueued
        )

        # Observe configuration changes
        Midi.Config.changed.connect(self.__config_change)
        Midi.Config.updated.connect(self.__config_update)

    @property
    def input(self):
        return self.__inputs[0]

    @property
    def output(self):
        return self.__outputs[0]

    def input_name(self):
        return self.input_names()[0]

    def input_names(self):
        names = Midi.Config.get("inputDevices", None)
        return names if names else [Midi.Config["inputDevice"] or self.__default_input]

    def output_name(self):
        return self.output_names()[0]

    def output_names(self):
        names = Midi.Config.get("outputDevices", None)
        return names if names else [Midi.Config["outputDevice"] or self.__default_output]

    def _on_port_removed(self):
        avail_names = self.backend.get_input_names()
        for port in self.__inputs:
            if port.is_open() and port.port_name() not in avail_names:
                logger.info(
                    translate(
                        "MIDIInfo", "MIDI port disconnected: '{}'"
                    ).format(port.port_name())
                )
                port.close()

        avail_names = self.backend.get_output_names()
        for port in self.__outputs:
            if port.is_open() and port.port_name() not in avail_names:
                logger.info(
                    translate(
                        "MIDIInfo", "MIDI port disconnected: '{}'"
                    ).format(port.port_name())
                )
                port.close()

    def _on_port_added(self):
        avail_names = self.backend.get_input_names()
        for port in self.__inputs:
            if not port.is_open() and port.port_name() in avail_names:
                self._reconnect(port, port.port_name(), avail_names)

        avail_names = self.backend.get_output_names()
        for port in self.__outputs:
            if not port.is_open() and port.port_name() in avail_names:
                self._reconnect(port, port.port_name(), avail_names)

    def _reconnect(self, midi: MIDIBase, current: str, available: list):
        if current in available:
            logger.info(
                translate("MIDIInfo", "Connecting to MIDI port: '{}'").format(
                    current
                )
            )
            midi.open()
        elif Midi.Config["connectByNameMatch"]:
            match = self._port_search_match(current, available)
            if match is not None:
                logger.info(
                    translate(
                        "MIDIInfo", "Connecting to matching MIDI port: '{}'"
                    ).format(match)
                )
                midi.change_port(match)

    def _port_search_match(self, to_match, available_names):
        # Strip client-id and port-id from the name
        simple_name = " ".join(to_match.split(" ")[:-1])

        for possible_match in available_names:
            if possible_match.startswith(simple_name):
                return possible_match

    def __config_change(self, key, _):
        if key == "inputDevice":
            self.__inputs[0].change_port(self.input_name())
        elif key == "outputDevice":
            self.__outputs[0].change_port(self.output_name())

    def __config_update(self, diff):
        if "inputDevice" in diff:
            self.__config_change("inputDevice", diff["inputDevice"])
        if "outputDevice" in diff:
            self.__config_change("outputDevice", diff["outputDevice"])
