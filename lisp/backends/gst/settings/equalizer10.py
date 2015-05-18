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

from PyQt5 import QtCore
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QGroupBox, QGridLayout, QLabel, QSlider

from lisp.backends.gst.elements.equalizer10 import Equalizer10
from lisp.ui.qvertiacallabel import QVerticalLabel
from lisp.ui.settings.section import SettingsSection


class Equalizer10Settings(SettingsSection):

    NAME = "Equalizer"
    ELEMENT = Equalizer10

    FREQ = ["30Hz", "60Hz", "120Hz", "240Hz", "475Hz", "950Hz", "1900Hz",
            "3800Hz", "7525Hz", "15KHz"]

    def __init__(self, size, Id, parent=None):
        super().__init__(size, parent)

        self.id = Id

        self.groupBox = QGroupBox(self)
        self.groupBox.resize(self.size())
        self.groupBox.setTitle("10 Bands Equalizer (IIR)")

        self.gridLayout = QGridLayout(self.groupBox)

        self.sliders = {}

        for n in range(10):
            label = QLabel(self.groupBox)
            width = QFontMetrics(label.font()).width('000')
            label.setMinimumWidth(width)
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setNum(0)
            self.gridLayout.addWidget(label, 0, n)

            slider = QSlider(self.groupBox)
            slider.setRange(-24, 12)
            slider.setPageStep(1)
            slider.setValue(0)
            slider.setOrientation(QtCore.Qt.Vertical)
            slider.valueChanged.connect(label.setNum)
            self.gridLayout.addWidget(slider, 1, n)
            self.gridLayout.setAlignment(slider, QtCore.Qt.AlignHCenter)
            self.sliders["band" + str(n)] = slider

            fLabel = QVerticalLabel(self.groupBox)
            fLabel.setAlignment(QtCore.Qt.AlignCenter)
            fLabel.setText(self.FREQ[n])
            self.gridLayout.addWidget(fLabel, 2, n)

        self.gridLayout.setRowStretch(0, 1)
        self.gridLayout.setRowStretch(1, 10)
        self.gridLayout.setRowStretch(2, 1)

    def enable_check(self, enable):
        self.groupBox.setCheckable(enable)
        self.groupBox.setChecked(False)

    def get_configuration(self):
        conf = {}

        if not (self.groupBox.isCheckable() and not self.groupBox.isChecked()):
            conf[self.id] = {}
            for band in self.sliders:
                conf[self.id][band] = self.sliders[band].value()

        return conf

    def set_configuration(self, conf):
        if conf is not None and self.id in conf:
            for band in self.sliders:
                if band in conf[self.id]:
                    self.sliders[band].setValue(conf[self.id][band])
