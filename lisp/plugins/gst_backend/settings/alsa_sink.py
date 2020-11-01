# This file is part of Linux Show Player
#
# Copyright 2020 Francesco Ceruti <ceppofrancy@gmail.com>
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
    QComboBox,
    QLabel,
    QVBoxLayout,
)
from pyalsa import alsacard

from lisp.plugins import get_plugin
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

        self.devices = {}
        self.discover_output_pcm_devices()

        self.deviceGroup = QGroupBox(self)
        self.deviceGroup.setGeometry(0, 0, self.width(), 100)
        self.deviceGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.deviceGroup)

        self.deviceComboBox = QComboBox(self.deviceGroup)
        for name, description in self.devices.items():
            self.deviceComboBox.addItem(description, name)

        self.deviceGroup.layout().addWidget(self.deviceComboBox)

        self.helpLabel = QLabel(self.deviceGroup)
        self.helpLabel.setWordWrap(True)
        self.deviceGroup.layout().addWidget(self.helpLabel)

        self.retranslateUi()

    def retranslateUi(self):
        self.deviceGroup.setTitle(translate("AlsaSinkSettings", "ALSA device"))
        self.helpLabel.setText(
            translate(
                "AlsaSinkSettings",
                "To make your custom PCM objects appear correctly in this list "
                "requires adding a 'hint.description' line to them.",
            )
        )

    def enableCheck(self, enabled):
        self.setGroupEnabled(self.deviceGroup, enabled)

    def loadSettings(self, settings):
        device = settings.get("device", "")
        if not device:
            device = get_plugin('GstBackend').Config.get('alsa_device', AlsaSink.FALLBACK_DEFAULT_DEVICE)

        self.deviceComboBox.setCurrentText(
            self.devices.get(device, self.devices.get(AlsaSink.FALLBACK_DEFAULT_DEVICE, ""))
        )

    def getSettings(self):
        if self.isGroupEnabled(self.deviceGroup):
            return {"device": self.deviceComboBox.currentData()}

        return {}

    def discover_output_pcm_devices(self):
        self.devices = {}

        # Get a list of the pcm devices "hints", the result is a combination of
        # "snd_device_name_hint()" and "snd_device_name_get_hint()"
        for pcm in alsacard.device_name_hint(-1, "pcm"):
            ioid = pcm.get("IOID")
            # Keep only bi-directional and output devices
            if ioid is None or ioid == "Output":
                self.devices[pcm["NAME"]] = pcm.get("DESC", pcm["NAME"])
