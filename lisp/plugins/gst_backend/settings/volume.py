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
    QDoubleSpinBox
)

from lisp.backend.audio_utils import db_to_linear, linear_to_db
from lisp.plugins.gst_backend.elements.volume import Volume
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate
from lisp.ui.widgets import QMuteButton


class VolumeSettings(SettingsPage):
    ELEMENT = Volume
    Name = ELEMENT.Name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.normalizedVolume = 1

        self.volumeGroup = QGroupBox(self)
        self.volumeGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.volumeGroup)

        self.muteButton = QMuteButton(self.volumeGroup)
        self.volumeGroup.layout().addWidget(self.muteButton)

        self.volumeSpinBox = QDoubleSpinBox(self.volumeGroup)
        self.volumeSpinBox.setRange(-100, 10)
        self.volumeSpinBox.setSuffix(" dB")
        self.volumeGroup.layout().addWidget(self.volumeSpinBox)

        # Resize the mute-button align with the adjacent input
        self.muteButton.setFixedHeight(self.volumeSpinBox.height())

        self.volumeLabel = QLabel(self.volumeGroup)
        self.volumeLabel.setAlignment(Qt.AlignCenter)
        self.volumeGroup.layout().addWidget(self.volumeLabel)

        self.volumeGroup.layout().setStretch(0, 1)
        self.volumeGroup.layout().setStretch(1, 3)
        self.volumeGroup.layout().setStretch(2, 4)

        self.normalizedGroup = QGroupBox(self)
        self.normalizedGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.normalizedGroup)

        self.normalizedLabel = QLabel(self.normalizedGroup)
        self.normalizedLabel.setAlignment(Qt.AlignCenter)
        self.normalizedGroup.layout().addWidget(self.normalizedLabel)

        self.normalizedReset = QCheckBox(self.normalizedGroup)
        self.normalizedGroup.layout().addWidget(self.normalizedReset)
        self.normalizedGroup.layout().setAlignment(
            self.normalizedReset, Qt.AlignCenter
        )

        self.retranslateUi()

    def retranslateUi(self):
        self.volumeGroup.setTitle(translate("VolumeSettings", "Volume"))
        self.volumeLabel.setText(translate("VolumeSettings", "Volume"))
        self.normalizedGroup.setTitle(
            translate("VolumeSettings", "Normalized volume")
        )
        self.normalizedLabel.setText("0.0 dB")
        self.normalizedReset.setText(translate("VolumeSettings", "Reset"))

    def enableCheck(self, enabled):
        self.setGroupEnabled(self.normalizedGroup, enabled)
        self.setGroupEnabled(self.volumeGroup, enabled)

    def getSettings(self):
        settings = {}

        if self.isGroupEnabled(self.volumeGroup):
            settings["volume"] = db_to_linear(self.volumeSpinBox.value())
            settings["mute"] = self.muteButton.isMute()
        if self.isGroupEnabled(self.normalizedGroup):
            if self.normalizedReset.isChecked():
                settings["normal_volume"] = 1
                # If the apply button is pressed, show the correct value
                self.normalizedLabel.setText("0 dB")
            else:
                settings["normal_volume"] = self.normalizedVolume

        return settings

    def loadSettings(self, settings):
        self.volumeSpinBox.setValue(linear_to_db(settings.get("volume", 1)))
        self.muteButton.setMute(settings.get("mute", False))

        self.normalizedVolume = settings.get("normal_volume", 1)
        self.normalizedLabel.setText(
            f"{linear_to_db(self.normalizedVolume):.3f} dB"
        )
