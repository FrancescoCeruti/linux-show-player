# This file is part of Linux Show Player
#
# Copyright 2024 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QGroupBox,
    QGridLayout,
    QLabel,
    QVBoxLayout,
    QSpinBox,
    QComboBox
)
from lisp.plugins.gst_backend.elements.highpass_filter import HighpassFilter
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class HighpassFilterSettings(SettingsPage):
    ELEMENT = HighpassFilter
    Name = ELEMENT.Name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.groupBox = QGroupBox(self)
        self.groupBox.resize(self.size())
        self.groupBox.setTitle(
            translate("HighpassFilterSettings", "Highpass Filter Settings")
        )
        self.groupBox.setLayout(QGridLayout())
        self.groupBox.layout().setVerticalSpacing(10)
        self.layout().addWidget(self.groupBox)

        # High-pass
        self.freqSpin = QSpinBox(self.groupBox)
        self.freqSpin.setRange(0, 20000)
        self.freqSpin.setMaximum(20000)
        self.freqSpin.setValue(30)
        self.freqSpin.setSuffix(" Hz")
        self.groupBox.layout().addWidget(self.freqSpin, 0, 0, 1, 1)

        fLabel = QLabel(self.groupBox)
        fLabel.setAlignment(QtCore.Qt.AlignCenter)
        fLabel.setText(translate("HighpassFilterSettings", "Cutoff Frequency"))
        self.groupBox.layout().addWidget(fLabel, 0, 1, 1, 1)


        # Window mode
        self.modeComboBox = QComboBox(self.groupBox)
        self.modeComboBox.addItem(
            translate("HighpassFilterSettings", "Hamming"), 0
        )
        self.modeComboBox.addItem(
            translate("HighpassFilterSettings", "Blackman"), 1
        )
        self.modeComboBox.addItem(
            translate("HighpassFilterSettings", "Gaussian"), 2
        )
        self.modeComboBox.addItem(
            translate("HighpassFilterSettings", "Cosine"), 3
        )
        self.modeComboBox.addItem(
            translate("HighpassFilterSettings", "Hann"), 4
        )
        self.groupBox.layout().addWidget(self.modeComboBox, 2, 0, 1, 1)
        
        wLabel = QLabel(self.groupBox)
        wLabel.setAlignment(QtCore.Qt.AlignCenter)
        wLabel.setText(translate("HighpassFilterSettings", "Window Mode"))
        self.groupBox.layout().addWidget(wLabel, 2, 1, 1, 1)


        # Presets
        self.presetsBox = QComboBox(self.groupBox)
        self.presetsBox.addItem(
            translate("HighpassFilterSettings", "Default"), 30
        )
        self.presetsBox.addItem(
            translate("HighpassFilterSettings", "Low vocal"), 126
        )
        self.presetsBox.addItem(
            translate("HighpassFilterSettings", "High vocal"), 113
        )
        self.presetsBox.addItem(
            translate("HighpassFilterSettings", "Telephone"), 300
        )
        self.presetsBox.addItem(
            translate("HighpassFilterSettings", "50 Hz line hum"), 50
        )
        self.presetsBox.addItem(
            translate("HighpassFilterSettings", "60 Hz line hum"), 60
        )
        self.presetsBox.addItem(
            translate("HighpassFilterSettings", "No Subwoofer"), 100
        )
        self.presetsBox.currentIndexChanged.connect(self.__preset)
        self.groupBox.layout().addWidget(self.presetsBox, 3, 0, 1, 1)
        
        pLabel = QLabel(self.groupBox)
        pLabel.setAlignment(QtCore.Qt.AlignCenter)
        pLabel.setText(translate("HighpassFilterSettings", "Presets"))
        self.groupBox.layout().addWidget(pLabel, 3, 1, 1, 1)
        
    def __preset(self, index):
        self.freqSpin.setValue(self.presetsBox.itemData(index))

    def enableCheck(self, enabled):
        self.setGroupEnabled(self.groupBox, enabled)

    def getSettings(self):
        if self.isGroupEnabled(self.groupBox):
            return {
                'cutoff': self.freqSpin.value(),
                'window': self.modeComboBox.currentData(),
                'mode': 1
            }

        return {}

    def loadSettings(self, settings):
        self.freqSpin.setValue(settings.get('cutoff', 0))
        self.modeComboBox.setCurrentIndex(int(settings.get('window', 0)))

