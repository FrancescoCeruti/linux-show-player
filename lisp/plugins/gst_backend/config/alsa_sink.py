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

from PyQt5.QtCore import QT_TRANSLATE_NOOP

from lisp.plugins.gst_backend.elements.alsa_sink import AlsaSink
from lisp.plugins.gst_backend.settings.alsa_sink import AlsaSinkSettings


class AlsaSinkConfig(AlsaSinkSettings):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "ALSA Default Device")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def loadSettings(self, settings):
        device = settings.get("alsa_device", AlsaSink.FALLBACK_DEFAULT_DEVICE)

        self.deviceComboBox.setCurrentText(
            self.devices.get(device, self.devices.get(AlsaSink.FALLBACK_DEFAULT_DEVICE, ""))
        )

    def getSettings(self):
        return {"alsa_device": self.deviceComboBox.currentData()}
