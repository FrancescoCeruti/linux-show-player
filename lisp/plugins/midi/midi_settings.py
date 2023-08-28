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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

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
        self.inputView.hasSelectionChange.connect(self.inputRemButton.setEnabled)
        self.inputRemButton.pressed.connect(self.inputView.removeSelectedPatch)
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
        self.outputView.hasSelectionChange.connect(self.outputRemButton.setEnabled)
        self.outputRemButton.pressed.connect(self.outputView.removeSelectedPatch)
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
        self.inputGroup.setTitle(translate("MIDISettings", "MIDI Inputs"))
        self.inputAddButton.setText(translate("MIDISettings", "Add"))
        self.inputRemButton.setText(translate("MIDISettings", "Remove"))

        self.outputGroup.setTitle(translate("MIDISettings", "MIDI Outputs"))
        self.outputAddButton.setText(translate("MIDISettings", "Add"))
        self.outputRemButton.setText(translate("MIDISettings", "Remove"))

        self.miscGroup.setTitle(translate("MIDISettings", "Misc options"))
        self.nameMatchCheckBox.setText(
            translate(
                "MIDISettings", "Try to connect using only device/port name"
            )
        )

    def loadSettings(self, settings):
        if "inputDevices" in settings:
            self.inputModel.deserialise(settings["inputDevices"])
            self.inputView.ensureOptionsExist(settings["inputDevices"])
        elif "inputDevice" in settings:
            self.inputModel.deserialise(settings["inputDevice"])
            self.inputView.ensureOptionExists(settings["inputDevice"])

        if "outputDevices" in settings:
            self.outputModel.deserialise(settings["outputDevices"])
            self.outputView.ensureOptionsExist(settings["outputDevices"])
        elif "outputDevice" in settings:
            self.outputModel.deserialise(settings["outputDevice"])
            self.outputView.ensureOptionExists(settings["outputDevice"])

        self.nameMatchCheckBox.setChecked(
            settings.get("connectByNameMatch", False)
        )

    def getSettings(self):
        if self.isEnabled():
            return {
                "inputDevices": self.inputModel.serialise(),
                "outputDevices": self.outputModel.serialise(),
                "connectByNameMatch": self.nameMatchCheckBox.isChecked(),
            }
        return {}

    def _updatePortsStatus(self):
        self.inputModel.updateStatuses()
        self.outputModel.updateStatuses()

    def _loadDevices(self):
        self.inputView.setOptions(midi_input_names())
        self.outputView.setOptions(midi_output_names())

    def _update(self):
        if self.isVisible():
            try:
                self._updatePortsStatus()
            except Exception:
                pass
