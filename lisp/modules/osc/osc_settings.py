# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
# Copyright 2012-2016 Thomas Achtner <info@offtools.de>
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


from PyQt5.QtCore import QT_TRANSLATE_NOOP, Qt
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QLabel,\
    QCheckBox, QHBoxLayout, QSpinBox, QLineEdit

from lisp.ui.ui_utils import translate
from lisp.core.configuration import config
from lisp.ui.settings.settings_page import SettingsPage
from lisp.modules.osc.osc_common import OscCommon


class OscSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'OSC settings')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.groupBox = QGroupBox(self)
        self.groupBox.setLayout(QVBoxLayout())
        self.groupBox.setTitle(
            translate('OscSettings', 'OSC Settings'))
        self.layout().addWidget(self.groupBox)

        self.enableModule = QCheckBox(self.groupBox)
        self.enableModule.setText(
            translate('OscSettings', 'enable OSC'))
        self.groupBox.layout().addWidget(self.enableModule)

        hbox = QHBoxLayout()
        self.inportBox = QSpinBox(self)
        self.inportBox.setMinimum(1000)
        self.inportBox.setMaximum(99999)
        label = QLabel(
            translate('OscSettings', 'Input Port:'))
        hbox.layout().addWidget(label)
        hbox.layout().addWidget(self.inportBox)
        self.groupBox.layout().addLayout(hbox)

        hbox = QHBoxLayout()
        self.outportBox = QSpinBox(self)
        self.outportBox.setMinimum(1000)
        self.outportBox.setMaximum(99999)
        label = QLabel(
            translate('OscSettings', 'Output Port:'))
        hbox.layout().addWidget(label)
        hbox.layout().addWidget(self.outportBox)
        self.groupBox.layout().addLayout(hbox)

        hbox = QHBoxLayout()
        self.hostnameEdit = QLineEdit()
        self.hostnameEdit.setText('localhost')
        self.hostnameEdit.setMaximumWidth(200)
        label = QLabel(
            translate('OscSettings', 'Hostname:'))
        hbox.layout().addWidget(label)
        hbox.layout().addWidget(self.hostnameEdit)
        self.groupBox.layout().addLayout(hbox)

        self.enableModule.stateChanged.connect(self.activate_module, Qt.QueuedConnection)
        self.inportBox.valueChanged.connect(self.change_inport, Qt.QueuedConnection)
        self.outportBox.valueChanged.connect(self.change_outport, Qt.QueuedConnection)
        self.hostnameEdit.textChanged.connect(self.change_hostname, Qt.QueuedConnection)

    def activate_module(self):
        if self.enableModule.isChecked():
            # start osc server
            OscCommon().start()
            # enable OSC Module in Settings
            config.set('OSC', 'enabled', 'True')
        else:
            # stop osc server
            OscCommon().stop()
            # disable OSC Module in Settings
            config.set('OSC', 'enabled', 'False')

    def change_inport(self):
        port = self.inportBox.value()
        if str(port) != config.get('OSC', 'inport'):
            config.set('OSC', 'inport', str(port))
            if self.enableModule.isChecked():
                self.enableModule.setChecked(False)

    def change_outport(self):
        port = self.outportBox.value()
        config.set('OSC', 'outport', str(port))

    def change_hostname(self):
        hostname = self.hostnameEdit.text()
        config.set('OSC', 'hostname', hostname)

    def get_settings(self):
        conf = {
            'enabled': str(self.enableModule.isChecked()),
            'inport': str(self.inportBox.value()),
            'outport': str(self.outportBox.value()),
            'hostname': str(self.hostnameEdit.text()),
        }
        return {'OSC': conf}

    def load_settings(self, settings):
        settings = settings.get('OSC', {})

        self.enableModule.setChecked(settings.get('enabled') == 'True')
        self.inportBox.setValue(int(settings.get('inport')))
        self.outportBox.setValue(int(settings.get('outport')))
        self.hostnameEdit.setText(settings.get('hostname'))
