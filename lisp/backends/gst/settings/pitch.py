# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2015 Francesco Ceruti <ceppofrancy@gmail.com>
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
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QSlider, QLabel

from lisp.backends.gst.elements.pitch import Pitch
from lisp.ui.settings.section import SettingsSection


class PitchSettings(SettingsSection):

    NAME = 'Pitch'
    ELEMENT = Pitch

    def __init__(self, size, Id, parent=None):
        super().__init__(size, parent)

        self.id = Id

        self.groupBox = QGroupBox(self)
        self.groupBox.setGeometry(0, 0, self.width(), 80)

        self.layout = QHBoxLayout(self.groupBox)

        self.pitchSlider = QSlider(self.groupBox)
        self.pitchSlider.setMinimum(-12)
        self.pitchSlider.setMaximum(12)
        self.pitchSlider.setPageStep(1)
        self.pitchSlider.setValue(0)
        self.pitchSlider.setOrientation(QtCore.Qt.Horizontal)
        self.pitchSlider.setTickPosition(QSlider.TicksAbove)
        self.pitchSlider.setTickInterval(1)
        self.layout.addWidget(self.pitchSlider)

        self.pitchLabel = QLabel(self.groupBox)
        self.pitchLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.pitchLabel)

        self.layout.setStretch(0, 3)
        self.layout.setStretch(1, 1)

        self.pitchSlider.valueChanged.connect(self.pitch_changed)

        self.retranslateUi()

    def retranslateUi(self):
        self.groupBox.setTitle("Pitch")
        self.pitchLabel.setText("+0 semitones")

    def enable_check(self, enable):
        self.groupBox.setCheckable(enable)
        self.groupBox.setChecked(False)

    def get_configuration(self):
        conf = {}

        if not (self.groupBox.isCheckable() and not self.groupBox.isChecked()):
            pitch = math.pow(2, self.pitchSlider.value() / 12)
            conf[self.id] = {'pitch': pitch}

        return conf

    def set_configuration(self, conf):
        if conf is not None and self.id in conf:
            self.pitchSlider.setValue(
                round(12 * math.log(conf[self.id]['pitch'], 2)))

    def pitch_changed(self, value):
        if value < 0:
            self.pitchLabel.setText(str(value) + ' semitones')
        else:
            self.pitchLabel.setText('+' + str(value) + ' semitones')
