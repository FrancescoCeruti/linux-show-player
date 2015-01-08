##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import *  # @UnusedWildImport

from lisp.gst.elements.alsa_sink import AlsaSink
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

    def sizeHint(self):
        return QSize(450, 100)

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
