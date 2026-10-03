# This file is part of Linux Show Player
#
# Copyright 2026 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import (
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QVBoxLayout,
)

from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class CueSearchSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "Cue Search")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.volumeGroup = QGroupBox(self)
        self.volumeGroup.setLayout(QGridLayout())
        self.volumeGroup.layout().setColumnStretch(0, 1)
        self.volumeGroup.layout().setColumnStretch(1, 1)
        self.layout().addWidget(self.volumeGroup)

        self.volumeUpLabel = QLabel(self.volumeGroup)
        self.volumeGroup.layout().addWidget(self.volumeUpLabel, 0, 0)
        self.volumeUpSpin = QDoubleSpinBox(self.volumeGroup)
        self.volumeUpSpin.setRange(1.0, 10.0)
        self.volumeUpSpin.setSingleStep(0.25)
        self.volumeUpSpin.setDecimals(2)
        self.volumeGroup.layout().addWidget(self.volumeUpSpin, 0, 1)

        self.volumeDownLabel = QLabel(self.volumeGroup)
        self.volumeGroup.layout().addWidget(self.volumeDownLabel, 1, 0)
        self.volumeDownSpin = QDoubleSpinBox(self.volumeGroup)
        self.volumeDownSpin.setRange(0.0, 1.0)
        self.volumeDownSpin.setSingleStep(0.05)
        self.volumeDownSpin.setDecimals(2)
        self.volumeGroup.layout().addWidget(self.volumeDownSpin, 1, 1)

        self.retranslateUi()

    def retranslateUi(self):
        self.volumeGroup.setTitle(translate("CueSearchSettings", "Volume multipliers"))
        self.volumeUpLabel.setText(translate("CueSearchSettings", "Volume up:"))
        self.volumeDownLabel.setText(translate("CueSearchSettings", "Volume down:"))

    def loadSettings(self, settings):
        self.volumeUpSpin.setValue(settings["volume"]["up"])
        self.volumeDownSpin.setValue(settings["volume"]["down"])

    def getSettings(self):
        return {
            "volume": {
                "up": self.volumeUpSpin.value(),
                "down": self.volumeDownSpin.value(),
            },
        }
