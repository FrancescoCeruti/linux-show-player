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
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QSlider, QLabel, QVBoxLayout

from lisp.plugins.gst_backend.elements.pitch import Pitch
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class PitchSettings(SettingsPage):
    ELEMENT = Pitch
    Name = ELEMENT.Name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.groupBox = QGroupBox(self)
        self.groupBox.setLayout(QHBoxLayout())
        self.layout().addWidget(self.groupBox)

        self.pitchSlider = QSlider(self.groupBox)
        self.pitchSlider.setMinimum(-12)
        self.pitchSlider.setMaximum(12)
        self.pitchSlider.setPageStep(1)
        self.pitchSlider.setValue(0)
        self.pitchSlider.setOrientation(QtCore.Qt.Horizontal)
        self.pitchSlider.setTickPosition(QSlider.TicksAbove)
        self.pitchSlider.setTickInterval(1)
        self.groupBox.layout().addWidget(self.pitchSlider)

        self.pitchLabel = QLabel(self.groupBox)
        self.pitchLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox.layout().addWidget(self.pitchLabel)

        self.groupBox.layout().setStretch(0, 3)
        self.groupBox.layout().setStretch(1, 1)

        self.pitchSlider.valueChanged.connect(self.pitch_changed)

        self.retranslateUi()

    def retranslateUi(self):
        self.groupBox.setTitle(translate("PitchSettings", "Pitch"))
        self.pitch_changed(0)

    def enableCheck(self, enabled):
        self.groupBox.setCheckable(enabled)
        self.groupBox.setChecked(False)

    def getSettings(self):
        if not (self.groupBox.isCheckable() and not self.groupBox.isChecked()):
            return {"pitch": math.pow(2, self.pitchSlider.value() / 12)}

        return {}

    def loadSettings(self, settings):
        self.pitchSlider.setValue(
            round(12 * math.log(settings.get("pitch", 1), 2))
        )

    def pitch_changed(self, value):
        self.pitchLabel.setText(
            translate("PitchSettings", "{0:+} semitones").format(value)
        )
