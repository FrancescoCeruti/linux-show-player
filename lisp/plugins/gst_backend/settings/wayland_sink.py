# This file is part of Linux Show Player
#
# Copyright 2024 Francesco Ceruti <ceppofrancy@gmail.com>
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
import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QGroupBox,
    QComboBox,
    QLabel,
    QCheckBox,
    QVBoxLayout,
)

from lisp.plugins.gst_backend import GstBackend
from lisp.plugins.gst_backend.elements.wayland_sink import WaylandSink
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class WaylandSinkSettings(SettingsPage):
    ELEMENT = WaylandSink
    Name = ELEMENT.Name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.devices = {
            'wayland-0': 'wayland-0',
            'wayland-1': 'wayland-1'
        }
        # self.discover_output_wayland_devices()

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

        self.fullScreen = QCheckBox(self.deviceGroup)
        self.deviceGroup.layout().addWidget(self.fullScreen)

        self.retranslateUi()

    def retranslateUi(self):
        self.deviceGroup.setTitle(translate("WaylandSinkSettings", "Video device"))
        self.helpLabel.setText(
            translate(
                "WaylandSinkSettings",
                "To make your custom PCM objects appear correctly in this list "
                "requires adding a 'hint.description' line to them.",
            )
        )
        self.fullScreen.setText(
            translate("VideoPlayerSettings", "Fullscreen")
        )

    def enableCheck(self, enabled):
        self.setGroupEnabled(self.deviceGroup, enabled)

    def loadSettings(self, settings):
        device = settings.get(
            "device",
            GstBackend.Config.get("wayland_device", "wayland-0"),
        )

        self.deviceComboBox.setCurrentText(
            self.devices.get(device, self.devices.get('wayland-0'))
        )

        self.fullScreen.setChecked(
            GstBackend.Config.get("fullscreen", True)
        )

    def getSettings(self):
        if self.isGroupEnabled(self.deviceGroup):
            return {
                "device": self.deviceComboBox.currentData(),
                "fullscreen": self.fullScreen.isChecked()
                }

        return {}

    def discover_output_wayland_devices(self):
        self.devices = {}

