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

from lisp.plugins.gst_backend.elements.video_balance import VideoBalance
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class VideoBalanceSettings(SettingsPage):
    ELEMENT = VideoBalance
    Name = ELEMENT.Name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.addBrightness()
        self.addConstrast()
        self.addHue()
        self.addSaturation()

        self.retranslateUi()

    def addBrightness(self):
        self.brightnessGroup = QGroupBox(self)
        self.brightnessGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.brightnessGroup)

        self.brightnessSlider = QSlider(self.brightnessGroup)
        self.brightnessSlider.setRange(-100, 100)
        self.brightnessSlider.setPageStep(1)
        self.brightnessSlider.setOrientation(Qt.Horizontal)
        self.brightnessSlider.valueChanged.connect(self.brightness_changed)
        self.brightnessGroup.layout().addWidget(self.brightnessSlider)

        self.brightnessLabel = QLabel(self.brightnessGroup)
        self.brightnessLabel.setAlignment(Qt.AlignCenter)
        self.brightnessGroup.layout().addWidget(self.brightnessLabel)

        self.brightnessGroup.layout().setStretch(0, 5)
        self.brightnessGroup.layout().setStretch(1, 1)

    def addConstrast(self):
        self.contrastGroup = QGroupBox(self)
        self.contrastGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.contrastGroup)

        self.contrastSlider = QSlider(self.contrastGroup)
        self.contrastSlider.setRange(0, 200)
        self.contrastSlider.setPageStep(1)
        self.contrastSlider.setOrientation(Qt.Horizontal)
        self.contrastSlider.valueChanged.connect(self.contrast_changed)
        self.contrastGroup.layout().addWidget(self.contrastSlider)

        self.contrastLabel = QLabel(self.contrastGroup)
        self.contrastLabel.setAlignment(Qt.AlignCenter)
        self.contrastGroup.layout().addWidget(self.contrastLabel)

        self.contrastGroup.layout().setStretch(0, 5)
        self.contrastGroup.layout().setStretch(1, 1)

    def addHue(self):
        self.hueGroup = QGroupBox(self)
        self.hueGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.hueGroup)

        self.hueSlider = QSlider(self.hueGroup)
        self.hueSlider.setRange(-100, 100)
        self.hueSlider.setPageStep(1)
        self.hueSlider.setOrientation(Qt.Horizontal)
        self.hueSlider.valueChanged.connect(self.hue_changed)
        self.hueGroup.layout().addWidget(self.hueSlider)

        self.hueLabel = QLabel(self.hueGroup)
        self.hueLabel.setAlignment(Qt.AlignCenter)
        self.hueGroup.layout().addWidget(self.hueLabel)

        self.hueGroup.layout().setStretch(0, 5)
        self.hueGroup.layout().setStretch(1, 1)

    def addSaturation(self):
        self.saturationGroup = QGroupBox(self)
        self.saturationGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.saturationGroup)

        self.saturationSlider = QSlider(self.saturationGroup)
        self.saturationSlider.setRange(0, 100)
        self.saturationSlider.setPageStep(1)
        self.saturationSlider.setOrientation(Qt.Horizontal)
        self.saturationSlider.valueChanged.connect(self.saturation_changed)
        self.saturationGroup.layout().addWidget(self.saturationSlider)

        self.saturationLabel = QLabel(self.saturationGroup)
        self.saturationLabel.setAlignment(Qt.AlignCenter)
        self.saturationGroup.layout().addWidget(self.saturationLabel)

        self.saturationGroup.layout().setStretch(0, 5)
        self.saturationGroup.layout().setStretch(1, 1)

    def retranslateUi(self):
        self.brightnessGroup.setTitle(translate("VideoBalanceSettings", "Brightness"))
        self.contrastGroup.setTitle(translate("VideoBalanceSettings", "Contrast"))
        self.hueGroup.setTitle(translate("VideoBalanceSettings", "Hue"))
        self.saturationGroup.setTitle(translate("VideoBalanceSettings", "Saturation"))

    def enableCheck(self, enabled):
        self.setGroupEnabled(self.brightnessGroup, enabled)
        self.setGroupEnabled(self.contrastGroup, enabled)
        self.setGroupEnabled(self.hueGroup, enabled)
        self.setGroupEnabled(self.saturationGroup, enabled)

    def getSettings(self):
        settings = {}

        if self.isGroupEnabled(self.brightnessGroup):
            settings["brightness"] = self.brightnessSlider.value() / 100
        if self.isGroupEnabled(self.contrastGroup):
            settings["contrast"] = self.contrastSlider.value() / 100
        if self.isGroupEnabled(self.hueGroup):
            settings["hue"] = self.hueSlider.value() / 100
        if self.isGroupEnabled(self.saturationGroup):
            settings["saturation"] = self.saturationSlider.value() / 100

        return settings

    def loadSettings(self, settings):
        self.brightnessSlider.setValue(int(settings.get("brightness", 0) * 100))
        self.contrastSlider.setValue(int(settings.get("contrast", 1) * 100))
        self.hueSlider.setValue(int(settings.get("hue", 0) * 100))
        self.saturationSlider.setValue(int(settings.get("saturation", 1) * 100))

        self.brightness_changed(self.brightnessSlider.value())
        self.contrast_changed(self.contrastSlider.value())
        self.hue_changed(self.hueSlider.value())
        self.saturation_changed(self.saturationSlider.value())

    def brightness_changed(self, value):
        self.brightnessLabel.setText(f"{value / 100}")

    def contrast_changed(self, value):
        self.contrastLabel.setText(f"{value / 100}")

    def hue_changed(self, value):
        self.hueLabel.setText(f"{value / 100}")

    def saturation_changed(self, value):
        self.saturationLabel.setText(f"{value / 100}")
