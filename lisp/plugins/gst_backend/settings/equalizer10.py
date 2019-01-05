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
from PyQt5.QtWidgets import QGroupBox, QGridLayout, QLabel, QSlider, QVBoxLayout

from lisp.plugins.gst_backend.elements.equalizer10 import Equalizer10
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class Equalizer10Settings(SettingsPage):
    ELEMENT = Equalizer10
    Name = ELEMENT.Name

    FREQ = [
        "30",
        "60",
        "120",
        "240",
        "475",
        "950",
        "1900",
        "3800",
        "7525",
        "15K",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.groupBox = QGroupBox(self)
        self.groupBox.resize(self.size())
        self.groupBox.setTitle(
            translate("Equalizer10Settings", "10 Bands Equalizer (IIR)")
        )
        self.groupBox.setLayout(QGridLayout())
        self.groupBox.layout().setVerticalSpacing(0)
        self.layout().addWidget(self.groupBox)

        self.sliders = {}

        for n in range(10):
            label = QLabel(self.groupBox)
            label.setMinimumWidth(QFontMetrics(label.font()).width("000"))
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setNum(0)
            self.groupBox.layout().addWidget(label, 0, n)

            slider = QSlider(self.groupBox)
            slider.setRange(-24, 12)
            slider.setPageStep(1)
            slider.setValue(0)
            slider.setOrientation(QtCore.Qt.Vertical)
            slider.valueChanged.connect(label.setNum)
            self.groupBox.layout().addWidget(slider, 1, n)
            self.groupBox.layout().setAlignment(slider, QtCore.Qt.AlignHCenter)
            self.sliders["band" + str(n)] = slider

            fLabel = QLabel(self.groupBox)
            fLabel.setStyleSheet("font-size: 8pt;")
            fLabel.setAlignment(QtCore.Qt.AlignCenter)
            fLabel.setText(self.FREQ[n])
            self.groupBox.layout().addWidget(fLabel, 2, n)

    def enableCheck(self, enabled):
        self.groupBox.setCheckable(enabled)
        self.groupBox.setChecked(False)

    def getSettings(self):
        settings = {}

        if not (self.groupBox.isCheckable() and not self.groupBox.isChecked()):
            for band in self.sliders:
                settings[band] = self.sliders[band].value()

        return settings

    def loadSettings(self, settings):
        for band in self.sliders:
            self.sliders[band].setValue(settings.get(band, 0))
