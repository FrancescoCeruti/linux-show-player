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
    QCheckBox, QComboBox, QHBoxLayout, QMessageBox, QSpinBox

from lisp.ui.mainwindow import MainWindow
from lisp.ui.settings.settings_page import CueSettingsPage,\
    SettingsPage
from lisp.utils import elogging
from lisp.utils.configuration import config
from lisp.ui.ui_utils import translate

from ola.OlaClient import OLADNotRunningException, OlaClient


class TimecodeSettings(SettingsPage):
    Name = 'Timecode Settings'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.behaviorsGroup = QGroupBox(self)
        self.behaviorsGroup.setLayout(QVBoxLayout())
        self.behaviorsGroup.setTitle(
            translate('TimecodeSettings', 'OLA Timecode Settings'))
        self.layout().addWidget(self.behaviorsGroup)

        self.activateBox = QCheckBox(self.behaviorsGroup)
        self.activateBox.setText(
            translate('TimecodeSettings', 'Enable Plugin'))
        self.behaviorsGroup.layout().addWidget(self.activateBox)

        self.comboLayout = QHBoxLayout()
        self.behaviorsGroup.layout().addLayout(self.comboLayout)
        self.formatLabel = QLabel(self.behaviorsGroup)
        self.comboLayout.addWidget(self.formatLabel)
        self.formatLabel.setText(
            translate('TimecodeSettings', 'Timecode Format:'))
        self.formatBox = QComboBox(self.behaviorsGroup)
        self.formatBox.addItem('FILM')
        self.formatBox.addItem('EBU')
        self.formatBox.addItem('SMPTE')
        self.comboLayout.addWidget(self.formatBox)

        self.activateBox.stateChanged.connect(self.testOla, Qt.QueuedConnection)

    def testOla(self):
        if self.activateBox.isChecked():
            try:
                client = OlaClient()
                del client
                config.set('Timecode', 'enabled', 'True')
            except OLADNotRunningException as e:
                elogging.warning('Plugin Timecode disabled', details=str(e), dialog=False)
                QMessageBox.warning(MainWindow(), 'Error', 'OLA is not running - Plugin is disabled,\n'
                                                           'start the OLA daemon to enable it.')
                self.activateBox.blockSignals(True)
                self.activateBox.setChecked(False)
                self.activateBox.blockSignals(False)

                config.set('Timecode', 'enabled', 'False')

    def get_settings(self):
        settings = {
            'enabled': str(self.activateBox.isChecked()),
            'format': str(self.formatBox.currentText())
        }

        return {'Timecode': settings}

    def load_settings(self, settings):
        settings = settings.get('Timecode', {})

        self.activateBox.setChecked(settings.get('enabled') == 'True')
        self.formatBox.setCurrentText(settings.get('format'))


class TimecodeCueSettings(CueSettingsPage):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'Timecode')

    def __init__(self, cue_class, **kwargs):
        super().__init__(cue_class, **kwargs)
        self.setLayout(QVBoxLayout())

        groupbox = QGroupBox(self)
        groupbox.setLayout(QVBoxLayout())
        groupbox.setAlignment(Qt.AlignTop)
        groupbox.setTitle("Timecode")
        self.layout().addWidget(groupbox)

        label = QLabel("to send ArtNet Timecode you need to setup a running OLA session!")
        groupbox.layout().addWidget(label)

        # enable / disable timecode
        self.tc_enable = QCheckBox("send ArtNet Timecode")
        self.tc_enable.setChecked(False)
        groupbox.layout().addWidget(self.tc_enable)

        # Hours can be replaced by cue number h:m:s:frames -> CUE:m:s:frames
        self.tc_usehours = QCheckBox("replace HOURS by a static track number")
        self.tc_usehours.setChecked(True)
        groupbox.layout().addWidget(self.tc_usehours)

        hbox = QHBoxLayout()

        self.tc_track = QSpinBox(self)
        self.tc_track.setMinimum(0)
        self.tc_track.setMaximum(99)
        hbox.layout().addWidget(self.tc_track)
        label = QLabel("track number")
        hbox.layout().addWidget(label)
        groupbox.layout().addLayout(hbox)

    def get_settings(self):
        conf = dict()
        conf['enabled'] = self.tc_enable.isChecked()
        conf['use_hours'] = self.tc_usehours.isChecked()
        conf['track'] = self.tc_track.value()
        return {'timecode': conf}

    def load_settings(self, settings):
        if settings is not None and 'timecode' in settings:
            conf = settings['timecode']
            if 'enabled' in conf:
                self.tc_enable.setChecked(conf['enabled'])
            if 'use_hours' in conf:
                self.tc_usehours.setChecked(conf['use_hours'])
            if 'track' in conf:
                self.tc_track.setValue(conf['track'])