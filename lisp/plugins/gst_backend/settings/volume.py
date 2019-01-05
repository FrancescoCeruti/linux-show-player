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
    QSlider,
    QLabel,
    QCheckBox,
    QVBoxLayout,
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

        self.normal = 1

        self.volumeBox = QGroupBox(self)
        self.volumeBox.setLayout(QHBoxLayout())
        self.layout().addWidget(self.volumeBox)

        self.muteButton = QMuteButton(self.volumeBox)
        self.volumeBox.layout().addWidget(self.muteButton)

        self.volume = QSlider(self.volumeBox)
        self.volume.setRange(-1000, 100)
        self.volume.setPageStep(1)
        self.volume.setOrientation(Qt.Horizontal)
        self.volume.valueChanged.connect(self.volume_changed)
        self.volumeBox.layout().addWidget(self.volume)

        self.volumeLabel = QLabel(self.volumeBox)
        self.volumeLabel.setAlignment(Qt.AlignCenter)
        self.volumeBox.layout().addWidget(self.volumeLabel)

        self.volumeBox.layout().setStretch(0, 1)
        self.volumeBox.layout().setStretch(1, 4)
        self.volumeBox.layout().setStretch(2, 1)

        self.normalBox = QGroupBox(self)
        self.normalBox.setLayout(QHBoxLayout())
        self.layout().addWidget(self.normalBox)

        self.normalLabel = QLabel(self.normalBox)
        self.normalLabel.setAlignment(Qt.AlignCenter)
        self.normalBox.layout().addWidget(self.normalLabel)

        self.normalReset = QCheckBox(self.normalBox)
        self.normalBox.layout().addWidget(self.normalReset)
        self.normalBox.layout().setAlignment(self.normalReset, Qt.AlignCenter)

        self.retranslateUi()

    def retranslateUi(self):
        self.volumeBox.setTitle(translate("VolumeSettings", "Volume"))
        self.volumeLabel.setText("0.0 dB")
        self.normalBox.setTitle(
            translate("VolumeSettings", "Normalized volume")
        )
        self.normalLabel.setText("0.0 dB")
        self.normalReset.setText(translate("VolumeSettings", "Reset"))

    def enableCheck(self, enabled):
        for box in [self.normalBox, self.volumeBox]:
            box.setCheckable(enabled)
            box.setChecked(False)

    def getSettings(self):
        settings = {}
        checkable = self.volumeBox.isCheckable()

        if not (checkable and not self.volumeBox.isChecked()):
            settings["volume"] = db_to_linear(self.volume.value() / 10)
            settings["mute"] = self.muteButton.isMute()
        if not (checkable and not self.normalBox.isChecked()):
            if self.normalReset.isChecked():
                settings["normal_volume"] = 1
                # If the apply button is pressed, show the correct value
                self.normalLabel.setText("0 dB")
            else:
                settings["normal_volume"] = self.normal

        return settings

    def loadSettings(self, settings):
        self.volume.setValue(linear_to_db(settings.get("volume", 1)) * 10)
        self.muteButton.setMute(settings.get("mute", False))
        self.normal = settings.get("normal_volume", 1)
        self.normalLabel.setText(
            str(round(linear_to_db(self.normal), 3)) + " dB"
        )

    def volume_changed(self, value):
        self.volumeLabel.setText(str(value / 10.0) + " dB")
