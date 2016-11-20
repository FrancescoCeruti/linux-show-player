# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
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
    QCheckBox, QComboBox, QHBoxLayout, QMessageBox, QSpinBox,\
    QLineEdit

from lisp.ui.ui_utils import translate
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

        self.enableFeedback = QCheckBox(self.groupBox)
        self.enableFeedback.setText(
            translate('OscSettings', 'enable Feedback'))
        self.groupBox.layout().addWidget(self.enableFeedback)

        hbox = QHBoxLayout()
        self.inportBox = QSpinBox(self)
        self.inportBox.setMinimum(1000)
        self.inportBox.setMaximum(99999)
        hbox.layout().addWidget(self.inportBox)
        label = QLabel(
            translate('OscSettings', 'Input Port'))
        hbox.layout().addWidget(label)
        self.groupBox.layout().addLayout(hbox)

        hbox = QHBoxLayout()
        self.outportBox = QSpinBox(self)
        self.outportBox.setMinimum(1000)
        self.outportBox.setMaximum(99999)
        hbox.layout().addWidget(self.outportBox)
        label = QLabel(
            translate('OscSettings', 'Input Port'))
        hbox.layout().addWidget(label)
        self.groupBox.layout().addLayout(hbox)

        hbox = QHBoxLayout()
        self.hostnameEdit = QLineEdit()
        self.hostnameEdit.setText('localhost')
        self.hostnameEdit.setMaximumWidth(200)
        hbox.layout().addWidget(self.hostnameEdit)
        label = QLabel(
            translate('OscSettings', 'Hostname'))
        hbox.layout().addWidget(label)
        self.groupBox.layout().addLayout(hbox)

    def get_settings(self):
        conf = {
            'enabled': str(self.enableCheck.isChecked()),
            'inport': str(self.inportBox.value()),
            'outport': str(self.outportBox.value()),
            'hostname': str(self.hostnameEdit.text()),
            'feedback': str(self.enableFeedback.isChecked())
        }
        return {'OSC': conf}

    def load_settings(self, settings):
        settings = settings.get('OSC', {})

        self.enableModule.setChecked(settings.get('enabled') == 'True')
        self.enableFeedback.setChecked(settings.get('feedback') == 'True')
        self.inportBox.setValue(int(settings.get('inport')))
        self.outportBox.setValue(int(settings.get('outport')))
        self.hostnameEdit.setText(settings.get('hostname'))
