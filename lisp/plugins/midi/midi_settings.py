# This file is part of Linux Show Player
#
# Copyright 2018 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QComboBox,
    QGridLayout,
    QLabel,
    QCheckBox,
    QSpacerItem,
)

from lisp.plugins import get_plugin
from lisp.plugins.midi.midi_utils import midi_input_names, midi_output_names
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
        self.portsGroup.layout().addWidget(self.outputStatus, 4, 1)

        self.portsGroup.layout().setColumnStretch(0, 2)
        self.portsGroup.layout().setColumnStretch(1, 3)

        self.miscGroup = QGroupBox(self)
        self.miscGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.miscGroup)

        self.nameMatchCheckBox = QCheckBox(self.miscGroup)
        self.miscGroup.layout().addWidget(self.nameMatchCheckBox)

        self.retranslateUi()

        try:
            plugin = get_plugin("Midi")
            self._loadDevices()

            inputStatus = MIDISettings.STATUS_SYMBOLS.get(
                plugin.input.is_open(), ""
            )
            self.inputStatus.setText(
                "[{}] {}".format(inputStatus, plugin.input.port_name())
            )

            outputStatus = MIDISettings.STATUS_SYMBOLS.get(
                plugin.output.is_open(), ""
            )
            self.outputStatus.setText(
                "[{}] {}".format(outputStatus, plugin.output.port_name())
            )
        except Exception:
            self.setEnabled(False)

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

    def loadSettings(self, settings):
        if settings["inputDevice"]:
            self.inputCombo.setCurrentText(settings["inputDevice"])
            if self.inputCombo.currentText() != settings["inputDevice"]:
                self.inputCombo.insertItem(
                    1, IconTheme.get("dialog-warning"), settings["inputDevice"]
                )
                self.inputCombo.setCurrentIndex(1)

        if settings["outputDevice"]:
            self.outputCombo.setCurrentText(settings["outputDevice"])
            if self.outputCombo.currentText() != settings["outputDevice"]:
                self.outputCombo.insertItem(
                    1, IconTheme.get("dialog-warning"), settings["outputDevice"]
                )
                self.outputCombo.setCurrentIndex(1)

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
                "connectByNameMatch": self.nameMatchCheckBox.isChecked(),
            }

        return {}

    def _loadDevices(self):
        self.inputCombo.clear()
        self.inputCombo.addItems(["Default"])
        self.inputCombo.addItems(midi_input_names())

        self.outputCombo.clear()
        self.outputCombo.addItems(["Default"])
        self.outputCombo.addItems(midi_output_names())
