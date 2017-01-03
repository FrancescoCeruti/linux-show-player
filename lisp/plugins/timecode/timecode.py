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
    QCheckBox, QSpinBox

import logging
from lisp.ui.ui_utils import translate
from lisp.application import Application
from lisp.core.configuration import config
from lisp.core.has_properties import Property
from lisp.core.plugin import Plugin
from lisp.core.signal import Connection
from lisp.cues.cue import Cue
from lisp.cues.media_cue import MediaCue
from lisp.ui.settings.settings_page import CueSettingsPage
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.modules.timecode.timecode_output import TimecodeOutput


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
            translate('TimecodeOutput',
                      'Replace HOURS by a static track number'))
        self.enableCheck.setText(
            translate('TimecodeOutput', 'Enable ArtNet Timecode'))
        self.trackLabel.setText(
            translate('TimecodeOutput', 'Track number'))
        self.warnLabel.setText(
            translate('TimecodeOutput',
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


class Timecode(Plugin):
    Name = 'Timecode'

    def __init__(self):
        super().__init__()
        self.__cues = set()

        # Register a new Cue property to store settings
        Cue.register_property('timecode', Property(default={}))

        # Register cue-settings-page
        CueSettingsRegistry().add_item(TimecodeSettings, MediaCue)

        # Watch cue-model changes
        Application().cue_model.item_added.connect(self.__cue_added)
        Application().cue_model.item_removed.connect(self.__cue_removed)

    def init(self):
        if not config['Timecode'].getboolean('enabled'):
            logging.info('TIMECODE: disabled by application settings')
        elif not TimecodeOutput().status():
            logging.info('TIMECODE: output not available')

    def reset(self):
        self.__cues.clear()
        TimecodeOutput().stop(rclient=True, rcue=True)

    def __cue_changed(self, cue, property_name, value):
        if property_name == 'timecode':
            if value.get('enabled', False):
                if cue.id not in self.__cues:
                    self.__cues.add(cue.id)
                    cue.started.connect(self.__cue_started, Connection.QtQueued)
            else:
                self.__cue_removed(cue)

    def __cue_added(self, cue):
        cue.property_changed.connect(self.__cue_changed)
        self.__cue_changed(cue, 'timecode', cue.timecode)

    def __cue_removed(self, cue):
        try:
            self.__cues.remove(cue.id)
            if TimecodeOutput().cue is cue:
                TimecodeOutput().stop(rcue=True)

            cue.started.disconnect(self.__cue_started)
            cue.property_changed.disconnect(self.__cue_changed)
        except KeyError:
            pass

    def __cue_started(self, cue):
        if config['Timecode'].getboolean('enabled'):
            if cue is not TimecodeOutput().cue:
                TimecodeOutput().start(cue)
        elif cue is TimecodeOutput().cue:
            TimecodeOutput().stop(rcue=True)
