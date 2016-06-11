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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QLabel, \
    QVBoxLayout, QDoubleSpinBox, QComboBox, QCheckBox

from lisp.cues.cue import CueNextAction
from lisp.ui.settings.settings_page import SettingsPage
from lisp.utils.util import translate


class CueGeneralSettings(SettingsPage):
    Name = 'Cue'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())

        # Pre wait
        self.preWaitGroup = QGroupBox(self)
        self.preWaitGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.preWaitGroup)

        self.preWaitSpin = QDoubleSpinBox(self.preWaitGroup)
        self.preWaitSpin.setMaximum(3600 * 24)
        self.preWaitGroup.layout().addWidget(self.preWaitSpin)

        self.preWaitLabel = QLabel(self.preWaitGroup)
        self.preWaitLabel.setAlignment(Qt.AlignCenter)
        self.preWaitGroup.layout().addWidget(self.preWaitLabel)

        # Post wait
        self.postWaitGroup = QGroupBox(self)
        self.postWaitGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.postWaitGroup)

        self.postWaitSpin = QDoubleSpinBox(self.postWaitGroup)
        self.postWaitSpin.setMaximum(3600 * 24)
        self.postWaitGroup.layout().addWidget(self.postWaitSpin)

        self.postWaitLabel = QLabel(self.postWaitGroup)
        self.postWaitLabel.setAlignment(Qt.AlignCenter)
        self.postWaitGroup.layout().addWidget(self.postWaitLabel)

        # Next action
        self.nextActionGroup = QGroupBox(self)
        self.nextActionGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.nextActionGroup)

        self.nextActionCombo = QComboBox(self.nextActionGroup)
        self.nextActionCombo.addItems([e.value for e in CueNextAction])
        self.nextActionGroup.layout().addWidget(self.nextActionCombo)

        # Checks
        self.stopPauseCheck = QCheckBox(self)
        self.layout().addWidget(self.stopPauseCheck)

        self.retranslateUi()

    def retranslateUi(self):
        self.preWaitGroup.setTitle(translate('CueSettings', 'Pre wait'))
        self.preWaitLabel.setText(translate('CueSettings',
                                            'Wait before cue execution'))
        self.postWaitGroup.setTitle(translate('CueSettings', 'Post wait'))
        self.postWaitLabel.setText(translate('CueSettings',
                                             'Wait after cue execution'))
        self.nextActionGroup.setTitle(translate('CueSettings', 'Next action'))
        self.stopPauseCheck.setText(translate('CueSettings',
                                              'Pause instead of stop'
                                              '(if supported)'))

    def load_settings(self, settings):
        if 'pre_wait' in settings:
            self.preWaitSpin.setValue(settings['pre_wait'])
        if 'post_wait' in settings:
            self.postWaitSpin.setValue(settings['post_wait'])
        if 'next_action' in settings:
            self.nextActionCombo.setCurrentText(settings['next_action'])
        if 'stop_pause' in settings:
            self.stopPauseCheck.setChecked(settings['stop_pause'])

    def enable_check(self, enable):
        self.preWaitGroup.setCheckable(enable)
        self.preWaitGroup.setChecked(False)

        self.postWaitGroup.setCheckable(enable)
        self.postWaitGroup.setChecked(False)

        self.nextActionGroup.setCheckable(enable)
        self.nextActionGroup.setChecked(False)

        self.stopPauseCheck.setTristate(enable)
        if enable:
            self.stopPauseCheck.setCheckState(Qt.PartiallyChecked)

    def get_settings(self):
        conf = {}
        checkable = self.preWaitGroup.isCheckable()

        if not (checkable and not self.preWaitGroup.isChecked()):
            conf['pre_wait'] = self.preWaitSpin.value()
        if not (checkable and not self.postWaitGroup.isChecked()):
            conf['post_wait'] = self.postWaitSpin.value()
        if not (checkable and not self.nextActionGroup.isChecked()):
            conf['next_action'] = self.nextActionCombo.currentText()
        if self.stopPauseCheck.checkState() != Qt.PartiallyChecked:
            conf['stop_pause'] = self.stopPauseCheck.isChecked()

        return conf
