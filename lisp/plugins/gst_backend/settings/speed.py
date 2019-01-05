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
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QSlider, QLabel, QVBoxLayout

from lisp.plugins.gst_backend.elements.speed import Speed
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class SpeedSettings(SettingsPage):
    ELEMENT = Speed
    Name = ELEMENT.Name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.groupBox = QGroupBox(self)
        self.groupBox.setLayout(QHBoxLayout())
        self.layout().addWidget(self.groupBox)

        self.speedSlider = QSlider(self.groupBox)
        self.speedSlider.setMinimum(1)
        self.speedSlider.setMaximum(1000)
        self.speedSlider.setPageStep(1)
        self.speedSlider.setValue(100)
        self.speedSlider.setOrientation(QtCore.Qt.Horizontal)
        self.speedSlider.setTickPosition(QSlider.TicksAbove)
        self.speedSlider.setTickInterval(10)
        self.groupBox.layout().addWidget(self.speedSlider)

        self.speedLabel = QLabel(self.groupBox)
        self.speedLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox.layout().addWidget(self.speedLabel)

        self.groupBox.layout().setStretch(0, 3)
        self.groupBox.layout().setStretch(1, 1)

        self.speedSlider.valueChanged.connect(self.speedChanged)

        self.retranslateUi()

    def retranslateUi(self):
        self.groupBox.setTitle(translate("SpeedSettings", "Speed"))
        self.speedLabel.setText("1.0")

    def enableCheck(self, enabled):
        self.groupBox.setCheckable(enabled)
        self.groupBox.setChecked(False)

    def getSettings(self):
        if not (self.groupBox.isCheckable() and not self.groupBox.isChecked()):
            return {"speed": self.speedSlider.value() / 100}

        return {}

    def loadSettings(self, settings):
        self.speedSlider.setValue(settings.get("speed", 1) * 100)

    def speedChanged(self, value):
        self.speedLabel.setText(str(value / 100.0))
