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
    QComboBox,
    QLabel,
    QVBoxLayout,
)

from lisp.plugins.gst_backend.elements.alsa_sink import AlsaSink
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class AlsaSinkSettings(SettingsPage):
    ELEMENT = AlsaSink
    Name = ELEMENT.Name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.devices = self._discover_pcm_devices()
        self.devices["default"] = "default"

        self.deviceGroup = QGroupBox(self)
        self.deviceGroup.setTitle(translate("AlsaSinkSettings", "ALSA device"))
        self.deviceGroup.setGeometry(0, 0, self.width(), 100)
        self.deviceGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.deviceGroup)

        self.device = QComboBox(self.deviceGroup)
        self.device.addItems(self.devices.keys())
        self.device.setCurrentText("default")
        self.device.setToolTip(
            translate(
                "AlsaSinkSettings",
                "ALSA devices, as defined in an " "asound configuration file",
            )
        )
        self.deviceGroup.layout().addWidget(self.device)

        self.label = QLabel(
            translate("AlsaSinkSettings", "ALSA device"), self.deviceGroup
        )
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.deviceGroup.layout().addWidget(self.label)

    def enableCheck(self, enabled):
        self.deviceGroup.setCheckable(enabled)
        self.deviceGroup.setChecked(False)

    def loadSettings(self, settings):
        device = settings.get("device", "default")

        for name, dev_name in self.devices.items():
            if device == dev_name:
                self.device.setCurrentText(name)
                break

    def getSettings(self):
        if not (
            self.deviceGroup.isCheckable() and not self.deviceGroup.isChecked()
        ):
            return {"device": self.devices[self.device.currentText()]}

        return {}

    def _discover_pcm_devices(self):
        devices = {}

        with open("/proc/asound/pcm", mode="r") as f:
            for dev in f.readlines():
                dev_name = dev[7 : dev.find(":", 7)].strip()
                dev_code = "hw:" + dev[:5].replace("-", ",")
                devices[dev_name] = dev_code

        return devices
