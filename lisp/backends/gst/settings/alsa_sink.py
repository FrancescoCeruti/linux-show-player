# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2015 Francesco Ceruti <ceppofrancy@gmail.com>
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
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QComboBox, QLabel

from lisp.backends.gst.elements.alsa_sink import AlsaSink
from lisp.ui.settings.section import SettingsSection


class AlsaSinkSettings(SettingsSection):

    NAME = "ALSA Sink"
    ELEMENT = AlsaSink

    def __init__(self, size, Id, parent=None):
        super().__init__(size, parent)

        self.id = Id
        self.devs = self._discover_pcm_devices()
        self.devs['default'] = 'default'

        self.group = QGroupBox(self)
        self.group.setTitle('ALSA device')
        self.group.setGeometry(0, 0, self.width(), 100)
        self.group.setLayout(QHBoxLayout())

        self.device = QComboBox(self.group)
        self.device.addItems(self.devs.keys())
        self.device.setCurrentText('default')
        self.device.setToolTip('ALSA device, as defined in an asound '
                               'configuration file')
        self.group.layout().addWidget(self.device)

        self.label = QLabel('ALSA device', self.group)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.group.layout().addWidget(self.label)

    def enable_check(self, enable):
        self.group.setCheckable(enable)
        self.group.setChecked(False)

    def set_configuration(self, conf):
        if self.id in conf:
            device = conf[self.id].get('device', 'default')
            for name in self.devs:
                if device == self.devs[name]:
                    self.device.setCurrentText(name)
                    break

    def get_configuration(self):
        if not (self.group.isCheckable() and not self.group.isChecked()):
            return {self.id: {'device': self.devs[self.device.currentText()]}}
        else:
            return {}

    def _discover_pcm_devices(self):
        devices = {}

        with open('/proc/asound/pcm', mode='r') as f:
            for dev in f.readlines():
                dev_name = dev[7:dev.find(':', 7)].strip()
                dev_code = 'hw:' + dev[:5].replace('-', ',')
                devices[dev_name] = dev_code

        return devices
