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
    QCheckBox, QSpinBox, QComboBox

from lisp.ui import elogging
from lisp.ui.ui_utils import translate
from lisp.core.configuration import config
from lisp.plugins.timecode.timecode_common import TcFormat
from lisp.plugins.timecode import protocols
from lisp.ui.settings.settings_page import SettingsPage
from lisp.ui.settings.settings_page import CueSettingsPage
from lisp.plugins.timecode.timecode_common import TimecodeCommon


class TimecodeSettings(CueSettingsPage):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'Timecode')

    def __init__(self, cue_class, **kwargs):
        super().__init__(cue_class, **kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.groupBox = QGroupBox(self)
        self.groupBox.setLayout(QGridLayout())
        self.layout().addWidget(self.groupBox)

        # enable / disable timecode
        self.enableCheck = QCheckBox(self.groupBox)
        self.enableCheck.setChecked(False)
        self.groupBox.layout().addWidget(self.enableCheck, 0, 0)

        # Hours can be replaced by cue number h:m:s:frames -> CUE:m:s:frames
        self.useHoursCheck = QCheckBox(self.groupBox)
        self.useHoursCheck.setChecked(True)
        self.groupBox.layout().addWidget(self.useHoursCheck, 1, 0)

        self.trackSpin = QSpinBox(self)
        self.trackSpin.setMinimum(0)
        self.trackSpin.setMaximum(99)
        self.useHoursCheck.stateChanged.connect(self.trackSpin.setEnabled)
        self.groupBox.layout().addWidget(self.trackSpin, 2, 0)

        self.trackLabel = QLabel(self.groupBox)
        self.trackLabel.setAlignment(Qt.AlignCenter)
        self.groupBox.layout().addWidget(self.trackLabel, 2, 1)

        self.layout().addSpacing(50)

        self.warnLabel = QLabel(self)
        self.warnLabel.setAlignment(Qt.AlignCenter)
        self.warnLabel.setStyleSheet('color: #FFA500; font-weight: bold')
        self.layout().addWidget(self.warnLabel)

        self.retranslateUi()

    def retranslateUi(self):
        self.groupBox.setTitle('Timecode')
        self.useHoursCheck.setText(
            translate('TimecodeSettings',
                      'Replace HOURS by a static track number'))
        self.enableCheck.setText(
            translate('TimecodeSettings', 'Enable Timecode'))
        self.trackLabel.setText(
            translate('TimecodeSettings', 'Track number'))
        if 'artnet' in config['Timecode']['protocol'].lower():
            self.warnLabel.setText(
                translate('TimecodeSettings'
                          '',
                          'To send ArtNet Timecode you need to setup a running OLA'
                          ' session!'))

    def get_settings(self):
        settings = {
            'enabled': self.enableCheck.isChecked(),
            'replace_hours': self.useHoursCheck.isChecked(),
            'track': self.trackSpin.value()
        }

        return {'timecode': settings}

    def load_settings(self, settings):
        settings = settings.get('timecode', {})
        self.enableCheck.setChecked(settings.get('enabled', False))
        self.useHoursCheck.setChecked(settings.get('replace_hours', False))
        self.trackSpin.setValue(settings.get('track', 0))


class TimecodeAppSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'Timecode Settings')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.groupBox = QGroupBox(self)
        self.groupBox.setLayout(QGridLayout())
        self.layout().addWidget(self.groupBox)

        self.formatLabel = QLabel(self.groupBox)
        self.groupBox.layout().addWidget(self.formatLabel, 0, 0)

        self.formatBox = QComboBox(self.groupBox)
        for fmt in TcFormat:
            self.formatBox.addItem(fmt.name)
        self.groupBox.layout().addWidget(self.formatBox, 0, 1)

        self.protocolLabel = QLabel(self.groupBox)
        self.groupBox.layout().addWidget(self.protocolLabel, 1, 0)

        self.protocolCombo = QComboBox(self.groupBox)
        for protocol in protocols.list_protocols():
            self.protocolCombo.addItem(protocol)
        self.groupBox.layout().addWidget(self.protocolCombo, 1, 1)

        self.retranslateUi()

    def retranslateUi(self):
        self.groupBox.setTitle(
            translate('TimecodeSettings', 'Timecode Settings'))
        self.formatLabel.setText(
            translate('TimecodeSettings', 'Timecode Format:'))
        self.protocolLabel.setText(
            translate('TimecodeSettings', 'Timecode Protocol:'))

    def __protocol_changed(self, protocol):
        # check for restart
        TimecodeCommon().change_protocol(protocol)

        print("__protocol_changed", protocol, TimecodeCommon().status)
        if not TimecodeCommon().status:
            elogging.error(
                translate('TimecodeSettings', 'Error on setting Timecode Protocol to {}.\n'
                                              'Timecode cannot be sent.\n'
                                              'Change the Protocol Entry.').format(protocol))

    def get_settings(self):
        conf = {}

        conf['format'] = self.formatBox.currentText()
        conf['protocol'] = self.protocolCombo.currentText()

        return {'Timecode': conf}

    def load_settings(self, settings):
        settings = settings.get('Timecode', {})

        self.formatBox.setCurrentText(settings.get('format', ''))
        self.protocolCombo.setCurrentText(settings.get('protocol', ''))
        self.protocolCombo.currentTextChanged.connect(self.__protocol_changed)
