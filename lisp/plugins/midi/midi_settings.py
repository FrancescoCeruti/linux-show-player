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

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP, QTimer
from PyQt5.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QComboBox,
    QGridLayout,
    QLabel,
    QCheckBox,
    QPushButton,
    QSpacerItem,
)

from lisp.plugins import get_plugin
from lisp.plugins.midi.midi_utils import midi_input_names, midi_output_names
from lisp.plugins.midi.midi_io_device_model import MidiInputDeviceModel, MidiOutputDeviceModel
from lisp.plugins.midi.midi_io_device_view import MidiIODeviceView
from lisp.ui.icons import IconTheme
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class MIDISettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "MIDI settings")
    STATUS_SYMBOLS = {True: "✓", False: "×"}  # U+2713, U+00D7

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.portsGroup = QGroupBox(self)
        self.portsGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.portsGroup)

        # Input port
        self.inputLabel = QLabel(self.portsGroup)
        self.portsGroup.layout().addWidget(self.inputLabel, 0, 0, 2, 1)

        self.inputCombo = QComboBox(self.portsGroup)
        self.portsGroup.layout().addWidget(self.inputCombo, 0, 1)

        self.inputStatus = QLabel(self.portsGroup)
        self.inputStatus.setDisabled(True)
        self.inputStatus.setText(f"[{MIDISettings.STATUS_SYMBOLS[False]}]")
        self.portsGroup.layout().addWidget(self.inputStatus, 1, 1)

        # Spacer
        self.portsGroup.layout().addItem(QSpacerItem(0, 30), 2, 0, 2, 1)

        # Output port
        self.outputLabel = QLabel(self.portsGroup)
        self.portsGroup.layout().addWidget(self.outputLabel, 3, 0, 2, 1)

        self.outputCombo = QComboBox(self.portsGroup)
        self.portsGroup.layout().addWidget(self.outputCombo, 3, 1)

        self.outputStatus = QLabel(self.portsGroup)
        self.outputStatus.setDisabled(True)
        self.outputStatus.setText(f"[{MIDISettings.STATUS_SYMBOLS[False]}]")
        self.portsGroup.layout().addWidget(self.outputStatus, 4, 1)

        self.portsGroup.layout().setColumnStretch(0, 2)
        self.portsGroup.layout().setColumnStretch(1, 3)

        # Input patches
        self.inputGroup = QGroupBox(self)
        self.inputGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.inputGroup)

        self.inputModel = MidiInputDeviceModel()
        self.inputView = MidiIODeviceView(self.inputModel, parent=self.inputGroup)
        self.inputGroup.layout().addWidget(self.inputView, 0, 0, 1, 2)

        self.inputAddButton = QPushButton(parent=self.inputGroup)
        self.inputAddButton.pressed.connect(self.inputModel.appendPatch)
        self.inputGroup.layout().addWidget(self.inputAddButton, 1, 0)

        self.inputRemButton = QPushButton(parent=self.inputGroup)
        self.inputRemButton.setEnabled(False)
        self.inputGroup.layout().addWidget(self.inputRemButton, 1, 1)

        # Output patches
        self.outputGroup = QGroupBox(self)
        self.outputGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.outputGroup)

        self.outputModel = MidiOutputDeviceModel()
        self.outputView = MidiIODeviceView(self.outputModel, parent=self.outputGroup)
        self.outputGroup.layout().addWidget(self.outputView, 0, 0, 1, 2)

        self.outputAddButton = QPushButton(parent=self.outputGroup)
        self.outputAddButton.pressed.connect(self.outputModel.appendPatch)
        self.outputGroup.layout().addWidget(self.outputAddButton, 1, 0)

        self.outputRemButton = QPushButton(parent=self.outputGroup)
        self.outputRemButton.setEnabled(False)
        self.outputGroup.layout().addWidget(self.outputRemButton, 1, 1)

        # Match by name
        self.miscGroup = QGroupBox(self)
        self.miscGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.miscGroup)

        self.nameMatchCheckBox = QCheckBox(self.miscGroup)
        self.miscGroup.layout().addWidget(self.nameMatchCheckBox)

        self.retranslateUi()

        try:
            self._updatePortsStatus()
            self._loadDevices()
        except Exception:
            self.setEnabled(False)
        else:
            # Update status every 2 seconds
            self.updateTimer = QTimer(self)
            self.updateTimer.timeout.connect(self._update)
            self.updateTimer.start(2000)

    def retranslateUi(self):
        self.portsGroup.setTitle(translate("MIDISettings", "MIDI devices"))
        self.inputLabel.setText(translate("MIDISettings", "Input"))
        self.outputLabel.setText(translate("MIDISettings", "Output"))

        self.miscGroup.setTitle(translate("MIDISettings", "Misc options"))
        self.nameMatchCheckBox.setText(
            translate(
                "MIDISettings", "Try to connect using only device/port name"
            )
        )

        self.inputGroup.setTitle(translate("MIDISettings", "MIDI Inputs"))
        self.inputAddButton.setText(translate("MIDISettings", "Add"))
        self.inputRemButton.setText(translate("MIDISettings", "Remove"))

        self.outputGroup.setTitle(translate("MIDISettings", "MIDI Outputs"))
        self.outputAddButton.setText(translate("MIDISettings", "Add"))
        self.outputRemButton.setText(translate("MIDISettings", "Remove"))

    def loadSettings(self, settings):
        if settings["inputDevice"]:
            self.inputCombo.setCurrentText(settings["inputDevice"])
            if self.inputCombo.currentText() != settings["inputDevice"]:
                self.inputCombo.insertItem(
                    1, IconTheme.get("dialog-warning"), settings["inputDevice"]
                )
                self.inputCombo.setCurrentIndex(1)

            if "inputDevices" not in settings:
                self.inputModel.deserialise(settings["inputDevice"])
                self.inputView.ensureOptionExists(settings["inputDevice"])

        if "inputDevices" in settings:
            self.inputModel.deserialise(settings["inputDevices"])
            self.inputView.ensureOptionsExist(settings["inputDevices"])

        if settings["outputDevice"]:
            self.outputCombo.setCurrentText(settings["outputDevice"])
            if self.outputCombo.currentText() != settings["outputDevice"]:
                self.outputCombo.insertItem(
                    1, IconTheme.get("dialog-warning"), settings["outputDevice"]
                )
                self.outputCombo.setCurrentIndex(1)

            if "outputDevices" not in settings:
                self.outputModel.deserialise(settings["outputDevice"])
                self.outputView.ensureOptionExists(settings["outputDevice"])

        if "outputDevices" in settings:
            self.outputModel.deserialise(settings["outputDevices"])
            self.outputView.ensureOptionsExist(settings["outputDevices"])

        self.nameMatchCheckBox.setChecked(
            settings.get("connectByNameMatch", False)
        )

    def getSettings(self):
        if self.isEnabled():
            input = self.inputCombo.currentText()
            output = self.outputCombo.currentText()

            return {
                "inputDevice": "" if input == "Default" else input,
                "outputDevice": "" if output == "Default" else output,
                "inputDevices": self.inputModel.serialise(),
                "outputDevices": self.outputModel.serialise(),
                "connectByNameMatch": self.nameMatchCheckBox.isChecked(),
            }

        return {}

    @staticmethod
    def portStatusSymbol(port):
        return MIDISettings.STATUS_SYMBOLS.get(port.is_open(), "")

    def _updatePortsStatus(self):
        midi = get_plugin("Midi")

        self.inputStatus.setText(
            f"[{self.portStatusSymbol(midi.input)}] {midi.input.port_name()}"
        )
        self.outputStatus.setText(
            f"[{self.portStatusSymbol(midi.output)}] {midi.output.port_name()}"
        )

        self.inputModel.updateStatuses()
        self.outputModel.updateStatuses()

    def _loadDevices(self):
        self.inputCombo.clear()
        self.inputCombo.addItems(["Default"])
        self.inputCombo.addItems(midi_input_names())

        self.outputCombo.clear()
        self.outputCombo.addItems(["Default"])
        self.outputCombo.addItems(midi_output_names())

        self.inputView.setOptions(midi_input_names())
        self.outputView.setOptions(midi_output_names())

    def _update(self):
        if self.isVisible():
            try:
                self._updatePortsStatus()
            except Exception:
                pass
