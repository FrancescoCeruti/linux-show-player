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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QGroupBox,
    QLabel,
    QSlider,
    QVBoxLayout,
    QHBoxLayout,
)

from lisp.plugins.gst_backend.elements.rotate import Rotate
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class RotateSettings(SettingsPage):
    ELEMENT = Rotate
    Name = ELEMENT.Name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.sigmaGroup = QGroupBox(self)
        self.sigmaGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.sigmaGroup)

        self.sigmaSlider = QSlider(self.sigmaGroup)
        self.sigmaSlider.setRange(-180, 180)
        self.sigmaSlider.setPageStep(1)
        self.sigmaSlider.setOrientation(Qt.Horizontal)
        self.sigmaSlider.valueChanged.connect(self.angle_changed)
        self.sigmaGroup.layout().addWidget(self.sigmaSlider)

        self.sigmaLabel = QLabel(self.sigmaGroup)
        self.sigmaLabel.setAlignment(Qt.AlignCenter)
        self.sigmaGroup.layout().addWidget(self.sigmaLabel)

        self.sigmaGroup.layout().setStretch(0, 5)
        self.sigmaGroup.layout().setStretch(1, 1)

        self.retranslateUi()

    def retranslateUi(self):
        self.sigmaGroup.setTitle(translate("RotateSettings", "Angle"))

    def enableCheck(self, enabled):
        self.setGroupEnabled(self.sigmaGroup, enabled)

    def getSettings(self):
        settings = {}

        if self.isGroupEnabled(self.sigmaGroup):
            settings["angle"] = math.radians(self.sigmaSlider.value())

        return settings

    def loadSettings(self, settings):
        self.sigmaSlider.setValue(int(math.degrees(settings.get("angle", 0))))

        self.angle_changed(self.sigmaSlider.value())

    def angle_changed(self, value):
        self.sigmaLabel.setText(
            f"{value}°\n"
            f"({translate('RotateSettings', 'clockwise') if value < 0 else translate('RotateSettings', 'counter-clockwise')})"
        )
