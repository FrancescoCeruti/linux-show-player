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
from PyQt5.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QDoubleSpinBox,
    QLabel,
    QVBoxLayout,
)

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

        self.speedSpinBox = QDoubleSpinBox(self.groupBox)
        self.speedSpinBox.setMinimum(0.1)
        self.speedSpinBox.setSingleStep(0.1)
        self.speedSpinBox.setMaximum(10)
        self.speedSpinBox.setValue(1)
        self.groupBox.layout().addWidget(self.speedSpinBox)

        self.speedLabel = QLabel(self.groupBox)
        self.speedLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox.layout().addWidget(self.speedLabel)

        self.retranslateUi()

    def retranslateUi(self):
        self.groupBox.setTitle(translate("SpeedSettings", "Speed"))
        self.speedLabel.setText(translate("SpeedSettings", "Speed"))

    def enableCheck(self, enabled):
        self.setGroupEnabled(self.groupBox, enabled)

    def getSettings(self):
        if self.isGroupEnabled(self.groupBox):
            return {"speed": self.speedSpinBox.value()}

        return {}

    def loadSettings(self, settings):
        self.speedSpinBox.setValue(settings.get("speed", 1))
