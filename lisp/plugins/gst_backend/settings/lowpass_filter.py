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

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import (
    QGroupBox,
    QGridLayout,
    QLabel,
    QSlider,
    QVBoxLayout,
    QSpinBox,
    QComboBox
)
from lisp.plugins.gst_backend.elements.lowpass_filter import LowpassFilter
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class LowpassFilterSettings(SettingsPage):
    ELEMENT = LowpassFilter
    Name = ELEMENT.Name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.groupBox = QGroupBox(self)
        self.groupBox.resize(self.size())
        self.groupBox.setTitle(
            translate("LowpassFilterSettings", "Lowpass Settings")
        )
        self.groupBox.setLayout(QGridLayout())
        self.groupBox.layout().setVerticalSpacing(0)
        self.layout().addWidget(self.groupBox)

        self.freqSpin = QSpinBox(self.groupBox)
        self.freqSpin.setRange(0, 20000)
        self.freqSpin.setMaximum(20000)
        self.freqSpin.setValue(110)
        self.groupBox.layout().addWidget(self.freqSpin, 0, 0)


        slider = QSlider(self.groupBox)
        slider.setRange(0, 20000)
        slider.setPageStep(1)
        slider.setValue(110)
        slider.setOrientation(QtCore.Qt.Horizontal)
        slider.valueChanged.connect(self.freqSpin.setValue)
        self.groupBox.layout().addWidget(slider, 1, 0)
        self.groupBox.layout().setAlignment(slider, QtCore.Qt.AlignVCenter)
        self.slider = slider
        self.freqSpin.valueChanged.connect(self.slider.setValue)


        fLabel = QLabel(self.groupBox)
        fLabel.setStyleSheet("font-size: 8pt;")
        fLabel.setAlignment(QtCore.Qt.AlignCenter)
        fLabel.setText(translate("LowpassFilterSettings", "Low-pass Frequency", "Low-pass Frequency"))
        self.groupBox.layout().addWidget(fLabel, 2, 0)

        self.modeComboBox = QComboBox(self.groupBox)
        self.modeComboBox.addItem(
            translate("LowpassFilterSettings", "Hamming"), 'hamming'
        )
        self.modeComboBox.addItem(
            translate("LowpassFilterSettings", "Blackman"), 'blackman'
        )
        self.modeComboBox.addItem(
            translate("LowpassFilterSettings", "Gaussian"), 'gaussian'
        )
        self.modeComboBox.addItem(
            translate("LowpassFilterSettings", "Cosine"), 'cosine'
        )
        self.modeComboBox.addItem(
            translate("LowpassFilterSettings", "Hann"), 'hann'
        )

        self.groupBox.layout().addWidget(self.modeComboBox, 3, 0, 1, 1)
        
        wLabel = QLabel(self.groupBox)
        wLabel.setStyleSheet("font-size: 8pt;")
        wLabel.setAlignment(QtCore.Qt.AlignCenter)
        wLabel.setText(translate("LowpassFilterSettings", "Windowing Mode"))
        self.groupBox.layout().addWidget(wLabel, 6, 0)

    def enableCheck(self, enabled):
        self.setGroupEnabled(self.groupBox, enabled)

    def getSettings(self):
        if self.isGroupEnabled(self.groupBox):
            return {
                'cutoff': self.slider.value(),
                'window': self.modeComboBox.currentData(),
                'mode': 0
            }

        return {}

    def loadSettings(self, settings):
        self.slider.setValue(settings.get('cutoff', 0))
        self.modeComboBox.setCurrentText(
            translate("LowpassFilterSettings", str(settings.get('window', 'hamming')).title())
        )

