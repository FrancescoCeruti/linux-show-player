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

import math

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QGroupBox,
    QGridLayout,
    QComboBox,
    QDoubleSpinBox,
    QLabel,
    QVBoxLayout,
)

from lisp.plugins.gst_backend.elements.audio_dynamic import AudioDynamic
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate

MIN_dB = 0.000_000_312  # -100dB


class AudioDynamicSettings(SettingsPage):
    ELEMENT = AudioDynamic
    Name = ELEMENT.Name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.groupBox = QGroupBox(self)
        self.groupBox.setGeometry(0, 0, self.width(), 240)
        self.groupBox.setLayout(QGridLayout())
        self.layout().addWidget(self.groupBox)

        # AudioDynamic mode
        self.modeComboBox = QComboBox(self.groupBox)
        self.modeComboBox.addItem(
            translate("AudioDynamicSettings", "Compressor"), "compressor"
        )
        self.modeComboBox.addItem(
            translate("AudioDynamicSettings", "Expander"), "expander"
        )
        self.groupBox.layout().addWidget(self.modeComboBox, 0, 0, 1, 1)

        self.modeLabel = QLabel(self.groupBox)
        self.modeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox.layout().addWidget(self.modeLabel, 0, 1, 1, 1)

        # AudioDynamic characteristic
        self.chComboBox = QComboBox(self.groupBox)
        self.chComboBox.addItem(
            translate("AudioDynamicSettings", "Soft Knee"), "soft-knee"
        )
        self.chComboBox.addItem(
            translate("AudioDynamicSettings", "Hard Knee"), "hard-knee"
        )
        self.groupBox.layout().addWidget(self.chComboBox, 1, 0, 1, 1)

        self.chLabel = QLabel(self.groupBox)
        self.chLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox.layout().addWidget(self.chLabel, 1, 1, 1, 1)

        # AudioDynamic ratio
        self.ratioSpin = QDoubleSpinBox(self.groupBox)
        self.groupBox.layout().addWidget(self.ratioSpin, 2, 0, 1, 1)

        self.ratioLabel = QLabel(self.groupBox)
        self.ratioLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox.layout().addWidget(self.ratioLabel, 2, 1, 1, 1)

        # AudioDynamic threshold
        self.thresholdSpin = QDoubleSpinBox(self.groupBox)
        self.thresholdSpin.setMaximum(0)
        self.thresholdSpin.setMinimum(-100)
        self.thresholdSpin.setSingleStep(1)
        self.groupBox.layout().addWidget(self.thresholdSpin, 3, 0, 1, 1)

        self.thresholdLabel = QLabel(self.groupBox)
        self.thresholdLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox.layout().addWidget(self.thresholdLabel, 3, 1, 1, 1)

        self.retranslateUi()

    def retranslateUi(self):
        self.groupBox.setTitle(
            translate("AudioDynamicSettings", "Compressor/Expander")
        )
        self.modeLabel.setText(translate("AudioDynamicSettings", "Type"))
        self.chLabel.setText(translate("AudioDynamicSettings", "Curve Shape"))
        self.ratioLabel.setText(translate("AudioDynamicSettings", "Ratio"))
        self.thresholdLabel.setText(
            translate("AudioDynamicSettings", "Threshold (dB)")
        )

    def enableCheck(self, enabled):
        self.groupBox.setCheckable(enabled)
        self.groupBox.setChecked(False)

    def getSettings(self):
        settings = {}

        if not (self.groupBox.isCheckable() and not self.groupBox.isChecked()):
            settings["ratio"] = self.ratioSpin.value()
            settings["threshold"] = math.pow(
                10, self.thresholdSpin.value() / 20
            )

            settings["mode"] = self.modeComboBox.currentData()
            settings["characteristics"] = self.chComboBox.currentData()

        return settings

    def loadSettings(self, settings):
        self.modeComboBox.setCurrentText(
            translate(
                "AudioDynamicSettings", settings.get("mode", "compressor")
            )
        )
        self.chComboBox.setCurrentText(
            translate(
                "AudioDynamicSettings",
                settings.get("characteristics", "soft-knee"),
            )
        )

        if settings.get("threshold", 0) == 0:
            settings["threshold"] = MIN_dB

        self.thresholdSpin.setValue(20 * math.log10(settings["threshold"]))
        self.ratioSpin.setValue(settings.get("ratio", 1))
