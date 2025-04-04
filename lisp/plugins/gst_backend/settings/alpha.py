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
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QVBoxLayout,
    QDoubleSpinBox,
)

from lisp.backend.audio_utils import db_to_linear, linear_to_db
from lisp.plugins.gst_backend.elements.alpha import Alpha
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate
from lisp.ui.widgets import QMuteButton


class AlphaSettings(SettingsPage):
    ELEMENT = Alpha
    Name = ELEMENT.Name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.alphaGroup = QGroupBox(self)
        self.alphaGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.alphaGroup)

        self.alphaSpinBox = QDoubleSpinBox(self.alphaGroup)
        self.alphaSpinBox.setRange(0, 1)
        self.alphaGroup.layout().addWidget(self.alphaSpinBox)

        self.alphaLabel = QLabel(self.alphaGroup)
        self.alphaLabel.setAlignment(Qt.AlignCenter)
        self.alphaGroup.layout().addWidget(self.alphaLabel)

        self.alphaGroup.layout().setStretch(0, 1)
        self.alphaGroup.layout().setStretch(1, 3)
        self.alphaGroup.layout().setStretch(2, 4)

        self.retranslateUi()

    def retranslateUi(self):
        self.alphaGroup.setTitle(translate("AlphaSettings", "Alpha"))
        self.alphaLabel.setText(translate("AlphaSettings", "AlphaSettings"))

    def enableCheck(self, enabled):
        self.setGroupEnabled(self.alphaGroup, enabled)

    def getSettings(self):
        settings = {}

        if self.isGroupEnabled(self.alphaGroup):
            settings["alpha"] = self.alphaSpinBox.value()

        return settings

    def loadSettings(self, settings):
        self.alphaSpinBox.setValue(settings.get("alpha", 1))
