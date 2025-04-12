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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QGroupBox,
    QLabel,
    QSlider,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
)

from lisp.plugins.gst_backend.elements.alpha import Alpha
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class AlphaSettings(SettingsPage):
    ELEMENT = Alpha
    Name = ELEMENT.Name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.backgroundGroup = QGroupBox(self)
        self.backgroundGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.backgroundGroup)

        self.backgroundComboBox = QComboBox(self.backgroundGroup)
        self.backgroundComboBox.addItem(
            translate("AlphaSettings", "Checkered Squares"), 0
        )
        self.backgroundComboBox.addItem(
            translate("AlphaSettings", "Black"), 1
        )
        self.backgroundComboBox.addItem(
            translate("AlphaSettings", "White"), 2
        )
        self.backgroundComboBox.addItem(
            translate("AlphaSettings", "Transparent"), 3
        )
        self.backgroundGroup.layout().addWidget(self.backgroundComboBox)

        self.alphaGroup = QGroupBox(self)
        self.alphaGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.alphaGroup)

        self.alphaSlider = QSlider(self.alphaGroup)
        self.alphaSlider.setRange(0, 100)
        self.alphaSlider.setPageStep(1)
        self.alphaSlider.setOrientation(Qt.Horizontal)
        self.alphaSlider.valueChanged.connect(self.alpha_changed)
        self.alphaGroup.layout().addWidget(self.alphaSlider)

        self.alphaLabel = QLabel(self.alphaGroup)
        self.alphaLabel.setAlignment(Qt.AlignCenter)
        self.alphaGroup.layout().addWidget(self.alphaLabel)

        self.alphaGroup.layout().setStretch(0, 5)
        self.alphaGroup.layout().setStretch(1, 1)

        self.retranslateUi()

    def retranslateUi(self):
        self.backgroundGroup.setTitle(translate("AlphaSettings", "Background"))
        self.alphaGroup.setTitle(translate("AlphaSettings", "Alpha"))

    def enableCheck(self, enabled):
        self.setGroupEnabled(self.alphaGroup, enabled)

    def getSettings(self):
        settings = {}

        if self.isGroupEnabled(self.alphaGroup):
            settings["alpha"] = self.alphaSlider.value() / 100
        if self.isGroupEnabled(self.backgroundGroup):
            settings["background"] = self.backgroundComboBox.currentData()

        return settings

    def loadSettings(self, settings):
        self.backgroundComboBox.setCurrentIndex(settings.get("background", 1))
        self.alphaSlider.setValue(int(settings.get("alpha", 1) * 100))

    def alpha_changed(self, value):
        self.alphaLabel.setText(f"{value / 100}")
