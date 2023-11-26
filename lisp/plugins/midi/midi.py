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
from lisp.core.signal import Connection, Signal
from lisp.plugins.midi.midi_cue import MidiCue
from lisp.plugins.midi.midi_io import MIDIOutput, MIDIInput, MIDIBase
from lisp.plugins.midi.midi_settings import MIDISettings
from lisp.plugins.midi.midi_utils import format_patch_name, midi_output_names, midi_input_names, PortDirection, PortNameMatch, PortStatus
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
        self.received = Signal()
        self.__inputs = {}
        for patch_id, device_name in self.input_patches().items():
            self._connect(patch_id, device_name, PortDirection.Input)

        # Create output handlers and connect
        self.__outputs = {}
        for patch_id, device_name in self.output_patches().items():
            self._connect(patch_id, device_name, PortDirection.Output)

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

    def add_exclusive_callback(self, patch_id, callback):
        if patch_id not in self.__inputs:
            return False
        handler = self.__inputs[patch_id]
        if handler.exclusive_mode:
            return False
        handler.exclusive_mode = True
        handler.received_exclusive.connect(callback)
        return True

    def remove_exclusive_callback(self, patch_id, callback):
        if patch_id not in self.__inputs:
            return
        handler = self.__inputs[patch_id]
        if handler.received_exclusive.is_connected_to(callback):
            handler.exclusive_mode = False
            handler.received_exclusive.disconnect(callback)

    def input_name(self, patch_id):
        return self.__inputs[patch_id].port_name()

    def input_name_formatted(self, patch_id):
        return format_patch_name(patch_id, self.__inputs[patch_id].port_name())

    def input_name_match(self, patch_id, candidate_name):
        if patch_id not in self.__inputs:
            return PortNameMatch.NoMatch
        port_name = self.__inputs[patch_id].port_name()
        if candidate_name == port_name:
            return PortNameMatch.ExactMatch
        if self.Config['connectByNameMatch'] and self._port_search_match(candidate_name, [port_name]):
            return PortNameMatch.FuzzyMatch
        return PortNameMatch.NoMatch

    def input_patches(self):
        patches = {}
        for k, v in Midi.Config.get("inputDevices", {}).items():
            if v is not None:
                patches[k] = v
        if not patches and Midi.Config.get("inputDevice", None) is not None:
            patches = { f"{PortDirection.Input.value}#1": Midi.Config.get("inputDevice", self.__default_input) }
        return patches

    def input_status(self, patch_id):
        if patch_id not in self.__inputs:
            return PortStatus.DoesNotExist
        return PortStatus.Open if self.__inputs[patch_id].is_open() else PortStatus.Closed

    def output_name(self, patch_id):
        return self.__outputs[patch_id].port_name()

    def output_name_formatted(self, patch_id):
        return format_patch_name(patch_id, self.__outputs[patch_id].port_name())

    def output_name_match(self, patch_id, candidate_name):
        if patch_id not in self.__outputs:
            return PortNameMatch.NoMatch
        port_name = self.__outputs[patch_id].port_name()
        if candidate_name == port_name:
            return PortNameMatch.ExactMatch
        if self.Config['connectByNameMatch'] and self._port_search_match(candidate_name, [port_name]):
            return PortNameMatch.FuzzyMatch
        return PortNameMatch.NoMatch

    def output_patches(self):
        patches = {}
        for k, v in Midi.Config.get("outputDevices", {}).items():
            if v is not None:
                patches[k] = v
        if not patches and Midi.Config.get("outputDevice", None) is not None:
            patches = { f"{PortDirection.Output.value}#1": Midi.Config.get("outputDevice", self.__default_output) }
        return patches

    def output_status(self, patch_id):
        if patch_id not in self.__outputs:
            return PortStatus.DoesNotExist
        return PortStatus.Open if self.__outputs[patch_id].is_open() else PortStatus.Closed

    def output_patch_exists(self, patch_id):
        return patch_id in self.__outputs

    def send(self, patch_id, message):
        self.__outputs[patch_id].send(message)

    def _on_port_removed(self):
        avail_names = self.backend.get_input_names()
        for port in self.__inputs.values():
            if port.is_open() and port.port_name() not in avail_names:
                logger.info(
                    translate(
                        "MIDIInfo", "MIDI port disconnected: '{}'"
                    ).format(port.port_name())
                )
                port.close()

        avail_names = self.backend.get_output_names()
        for port in self.__outputs.values():
            if port.is_open() and port.port_name() not in avail_names:
                logger.info(
                    translate(
                        "MIDIInfo", "MIDI port disconnected: '{}'"
                    ).format(port.port_name())
                )
                port.close()

    def _on_port_added(self):
        avail_names = self.backend.get_input_names()
        for port in self.__inputs.values():
            if not port.is_open() and port.port_name() in avail_names:
                self._reconnect(port, port.port_name(), avail_names)

        avail_names = self.backend.get_output_names()
        for port in self.__outputs.values():
            if not port.is_open() and port.port_name() in avail_names:
                self._reconnect(port, port.port_name(), avail_names)

    def _dispatch_message(self, patch_id, message):
        self.received.emit(patch_id, message)

    def _connect(self, patch_id, device_name, direction: PortDirection):
        if direction is PortDirection.Input:
            available = self.backend.get_input_names()
            self.__inputs[patch_id] = MIDIInput(self.backend, patch_id, device_name)
            self.__inputs[patch_id].received.connect(self._dispatch_message)
            self._reconnect(self.__inputs[patch_id], device_name, available)
        elif direction is PortDirection.Output:
            available = self.backend.get_output_names()
            self.__outputs[patch_id] = MIDIOutput(self.backend, patch_id, device_name)
            self._reconnect(self.__outputs[patch_id], device_name, available)

    def _disconnect(self, patch_id, direction: PortDirection):
        if direction is PortDirection.Input:
            self.__inputs[patch_id].close()
            del self.__inputs[patch_id]
        elif direction is PortDirection.Output:
            self.__outputs[patch_id].close()
            del self.__outputs[patch_id]

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

    def __config_change(self, key, changeset):
        if key == "inputDevices":
            for patch_id, device_name in changeset.items():
                if patch_id not in self.__inputs:
                    self._connect(patch_id, device_name, PortDirection.Input)
                elif device_name is None:
                    self._disconnect(patch_id, PortDirection.Input)
                else:
                    self.__inputs[patch_id].change_port(device_name or self.__default_input)
        elif key == "outputDevices":
            for patch_id, device_name in changeset.items():
                if patch_id not in self.__outputs:
                    self._connect(patch_id, device_name, PortDirection.Output)
                elif device_name is None:
                    self._disconnect(patch_id, PortDirection.Output)
                else:
                    self.__outputs[patch_id].change_port(device_name or self.__default_output)

    def __config_update(self, diff):
        if "inputDevices" in diff:
            self.__config_change("inputDevices", diff["inputDevices"])
        if "outputDevices" in diff:
            self.__config_change("outputDevices", diff["outputDevices"])
