# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
# Copyright 2016 Thomas Achtner <info@offtools.de>
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
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QLabel,\
    QCheckBox, QComboBox

from lisp.core.configuration import config
from lisp.ui.settings.settings_page import SettingsPage
from lisp.modules.timecode import backends
from lisp.ui.ui_utils import translate
from lisp.modules.timecode.timecode_output import TcFormat, TimecodeOutput


class TimecodeSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'Timecode Settings')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.groupBox = QGroupBox(self)
        self.groupBox.setLayout(QGridLayout())
        self.layout().addWidget(self.groupBox)

        self.activateBox = QCheckBox(self.groupBox)
        self.groupBox.layout().addWidget(self.activateBox, 0, 0)

        self.hresBox = QCheckBox(self.groupBox)
        self.groupBox.layout().addWidget(self.hresBox, 1, 0)

        self.formatLabel = QLabel(self.groupBox)
        self.groupBox.layout().addWidget(self.formatLabel, 2, 0)

        self.formatBox = QComboBox(self.groupBox)
        for fmt in TcFormat:
            self.formatBox.addItem(fmt.name)
        self.groupBox.layout().addWidget(self.formatBox, 2, 1)

        self.backendLabel = QLabel(self.groupBox)
        self.groupBox.layout().addWidget(self.backendLabel, 3, 0)

        self.backendBox = QComboBox(self.groupBox)
        for backend in backends.list_backends():
            self.backendBox.addItem(backend)
        self.groupBox.layout().addWidget(self.backendBox, 3, 1)

        self.retranslateUi()

    def retranslateUi(self):
        self.groupBox.setTitle(
            translate('TimecodeSettings', 'Timecode Settings'))
        self.activateBox.setText(translate('TimecodeSettings', 'Enable Plugin'))
        self.hresBox.setText(
            translate('TimecodeSettings', 'High-Resolution Timecode'))
        self.formatLabel.setText(
            translate('TimecodeSettings', 'Timecode Format:'))
        self.backendLabel.setText(
            translate('TimecodeSettings', 'Timecode Backend:'))

    def get_settings(self):
        conf = {}
        enabled = self.activateBox.isChecked()
        hres = self.hresBox.isChecked()
        fmt = self.formatBox.currentText()
        backend = self.backendBox.currentText()

        # check for restart
        if enabled and (not config['Timecode'].getboolean('enabled') or backend != config['Timecode']['backend']):
            TimecodeOutput().change_backend(backend)
            if not TimecodeOutput().status():
                enabled = False

        conf['enabled'] = str(enabled)
        conf['hres'] = str(hres)
        conf['format'] = fmt
        conf['backend'] = backend

        return {'Timecode': conf}

    def load_settings(self, settings):
        settings = settings.get('Timecode', {})

        self.activateBox.setChecked(settings.get('enabled') == 'True')
        self.hresBox.setChecked(settings.get('hres') == 'True')
        self.formatBox.setCurrentText(settings.get('format', ''))
        self.backendBox.setCurrentText(settings.get('backend', ''))
