# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2017 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QComboBox,\
    QVBoxLayout, QDoubleSpinBox, QTabWidget, QWidget

from lisp.cues.cue import CueNextAction, CueAction
from lisp.ui.settings.settings_page import CueSettingsPage
from lisp.ui.ui_utils import translate
from lisp.ui.widgets import FadeComboBox
from lisp.ui.widgets.fade_edit import FadeEdit


class CueGeneralSettings(CueSettingsPage):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'Cue')

    def __init__(self, cue_class, **kwargs):
        super().__init__(cue_class, **kwargs)
        self.setLayout(QVBoxLayout())

        self.tabWidget = QTabWidget(self)
        self.layout().addWidget(self.tabWidget)

        # TAB 1 (Behaviours)
        self.tab_1 = QWidget(self.tabWidget)
        self.tab_1.setLayout(QVBoxLayout())
        self.tabWidget.addTab(self.tab_1, '1')

        # Start-Action
        self.startActionGroup = QGroupBox(self.tab_1)
        self.startActionGroup.setLayout(QHBoxLayout())
        self.tab_1.layout().addWidget(self.startActionGroup)

        self.startActionCombo = QComboBox(self.startActionGroup)
        for action in [CueAction.Start, CueAction.FadeInStart]:
            if action in cue_class.CueActions:
                self.startActionCombo.addItem(
                    translate('CueAction', action.name), action.value)
        self.startActionCombo.setEnabled(self.startActionCombo.count() > 1)
        self.startActionGroup.layout().addWidget(self.startActionCombo)

        self.startActionLabel = QLabel(self.startActionGroup)
        self.startActionLabel.setAlignment(Qt.AlignCenter)
        self.startActionGroup.layout().addWidget(self.startActionLabel)

        # Stop-Action
        self.stopActionGroup = QGroupBox(self.tab_1)
        self.stopActionGroup.setLayout(QHBoxLayout())
        self.tab_1.layout().addWidget(self.stopActionGroup)

        self.stopActionCombo = QComboBox(self.stopActionGroup)
        for action in [CueAction.Stop, CueAction.Pause,
                       CueAction.FadeOutStop, CueAction.FadeOutPause]:
            if action in cue_class.CueActions:
                self.stopActionCombo.addItem(
                    translate('CueAction', action.name), action.value)
        self.stopActionCombo.setEnabled(self.stopActionCombo.count() > 1)
        self.stopActionGroup.layout().addWidget(self.stopActionCombo)

        self.stopActionLabel = QLabel(self.stopActionGroup)
        self.stopActionLabel.setAlignment(Qt.AlignCenter)
        self.stopActionGroup.layout().addWidget(self.stopActionLabel)

        self.tab_1.layout().addSpacing(150)
        self.tab_1.setEnabled(self.stopActionCombo.isEnabled() and
                              self.startActionCombo.isEnabled())

        # TAB 2 (Pre/Post Wait)
        self.tab_2 = QWidget(self.tabWidget)
        self.tab_2.setLayout(QVBoxLayout())
        self.tabWidget.addTab(self.tab_2, '2')

        # Pre wait
        self.preWaitGroup = QGroupBox(self.tab_2)
        self.preWaitGroup.setLayout(QHBoxLayout())
        self.tab_2.layout().addWidget(self.preWaitGroup)

        self.preWaitSpin = QDoubleSpinBox(self.preWaitGroup)
        self.preWaitSpin.setMaximum(3600 * 24)
        self.preWaitGroup.layout().addWidget(self.preWaitSpin)

        self.preWaitLabel = QLabel(self.preWaitGroup)
        self.preWaitLabel.setAlignment(Qt.AlignCenter)
        self.preWaitGroup.layout().addWidget(self.preWaitLabel)

        # Post wait
        self.postWaitGroup = QGroupBox(self.tab_2)
        self.postWaitGroup.setLayout(QHBoxLayout())
        self.tab_2.layout().addWidget(self.postWaitGroup)

        self.postWaitSpin = QDoubleSpinBox(self.postWaitGroup)
        self.postWaitSpin.setMaximum(3600 * 24)
        self.postWaitGroup.layout().addWidget(self.postWaitSpin)

        self.postWaitLabel = QLabel(self.postWaitGroup)
        self.postWaitLabel.setAlignment(Qt.AlignCenter)
        self.postWaitGroup.layout().addWidget(self.postWaitLabel)

        # Next action
        self.nextActionGroup = QGroupBox(self.tab_2)
        self.nextActionGroup.setLayout(QHBoxLayout())
        self.tab_2.layout().addWidget(self.nextActionGroup)

        self.nextActionCombo = QComboBox(self.nextActionGroup)
        for action in CueNextAction:
            self.nextActionCombo.addItem(
                translate('CueNextAction', action.name), action.value)
        self.nextActionGroup.layout().addWidget(self.nextActionCombo)

        # TAB 3 (Fade In/Out)
        self.tab_3 = QWidget(self.tabWidget)
        self.tab_3.setLayout(QVBoxLayout())
        self.tabWidget.addTab(self.tab_3, '3')

        # FadeIn
        self.fadeInGroup = QGroupBox(self.tab_3)
        self.fadeInGroup.setEnabled(
            CueAction.FadeInStart in cue_class.CueActions
        )
        self.fadeInGroup.setLayout(QHBoxLayout())
        self.tab_3.layout().addWidget(self.fadeInGroup)

        self.fadeInEdit = FadeEdit(self.fadeInGroup,
                                   mode=FadeComboBox.Mode.FadeIn)
        self.fadeInGroup.layout().addWidget(self.fadeInEdit)

        # FadeOut
        self.fadeOutGroup = QGroupBox(self.tab_3)
        self.fadeOutGroup.setEnabled(
            CueAction.FadeOutPause in cue_class.CueActions or
            CueAction.FadeOutStop in cue_class.CueActions
        )
        self.fadeOutGroup.setLayout(QHBoxLayout())
        self.tab_3.layout().addWidget(self.fadeOutGroup)

        self.fadeOutEdit = FadeEdit(self.fadeOutGroup,
                                    mode=FadeComboBox.Mode.FadeOut)
        self.fadeOutGroup.layout().addWidget(self.fadeOutEdit)

        self.retranslateUi()

    def retranslateUi(self):
        # Tabs
        self.tabWidget.setTabText(0, translate('CueSettings', 'Behaviours'))
        self.tabWidget.setTabText(1, translate('CueSettings', 'Pre/Post Wait'))
        self.tabWidget.setTabText(2, translate('CueSettings', 'Fade In/Out'))

        # Start-Action
        self.startActionGroup.setTitle(
            translate('CueSettings', 'Start action'))
        self.startActionLabel.setText(
            translate('CueSettings', 'Default action to start the cue'))
        # Stop-Action
        self.stopActionGroup.setTitle(
            translate('CueSettings', 'Stop action'))
        self.stopActionLabel.setText(
            translate('CueSettings', 'Default action to stop the cue'))

        # PreWait
        self.preWaitGroup.setTitle(translate('CueSettings', 'Pre wait'))
        self.preWaitLabel.setText(
            translate('CueSettings', 'Wait before cue execution'))
        # PostWait
        self.postWaitGroup.setTitle(translate('CueSettings', 'Post wait'))
        self.postWaitLabel.setText(
            translate('CueSettings', 'Wait after cue execution'))
        # NextAction
        self.nextActionGroup.setTitle(translate('CueSettings', 'Next action'))

        # FadeIn/Out
        self.fadeInGroup.setTitle(translate('FadeSettings', 'Fade In'))
        self.fadeOutGroup.setTitle(translate('FadeSettings', 'Fade Out'))

    def load_settings(self, settings):
        self.startActionCombo.setCurrentText(
            translate('CueAction', settings.get('default_start_action', '')))
        self.stopActionCombo.setCurrentText(
            translate('CueAction', settings.get('default_stop_action', '')))

        self.preWaitSpin.setValue(settings.get('pre_wait', 0))
        self.postWaitSpin.setValue(settings.get('post_wait', 0))
        self.nextActionCombo.setCurrentText(
            translate('CueNextAction', settings.get('next_action', '')))

        self.fadeInEdit.setFadeType(settings.get('fadein_type', ''))
        self.fadeInEdit.setDuration(settings.get('fadein_duration', 0))
        self.fadeOutEdit.setFadeType(settings.get('fadeout_type', ''))
        self.fadeOutEdit.setDuration(settings.get('fadeout_duration', 0))

    def enable_check(self, enable):
        self.startActionGroup.setCheckable(enable)
        self.startActionGroup.setChecked(False)
        self.stopActionGroup.setCheckable(enable)
        self.stopActionGroup.setChecked(False)

        self.preWaitGroup.setCheckable(enable)
        self.preWaitGroup.setChecked(False)
        self.postWaitGroup.setCheckable(enable)
        self.postWaitGroup.setChecked(False)
        self.nextActionGroup.setCheckable(enable)
        self.nextActionGroup.setChecked(False)

        self.fadeInGroup.setCheckable(enable)
        self.fadeInGroup.setChecked(False)
        self.fadeOutGroup.setCheckable(enable)
        self.fadeOutGroup.setChecked(False)

    def get_settings(self):
        conf = {}
        checkable = self.preWaitGroup.isCheckable()

        if not (checkable and not self.startActionGroup.isChecked()):
            if self.startActionCombo.isEnabled():
                conf['default_start_action'] = self.startActionCombo.currentData()
        if not (checkable and not self.stopActionGroup.isChecked()):
            if self.stopActionCombo.isEnabled():
                conf['default_stop_action'] = self.stopActionCombo.currentData()

        if not (checkable and not self.preWaitGroup.isChecked()):
            conf['pre_wait'] = self.preWaitSpin.value()
        if not (checkable and not self.postWaitGroup.isChecked()):
            conf['post_wait'] = self.postWaitSpin.value()
        if not (checkable and not self.nextActionGroup.isChecked()):
            conf['next_action'] = self.nextActionCombo.currentData()

        if not (checkable and not self.fadeInGroup.isChecked()):
            conf['fadein_type'] = self.fadeInEdit.fadeType()
            conf['fadein_duration'] = self.fadeInEdit.duration()
        if not (checkable and not self.fadeInGroup.isChecked()):
            conf['fadeout_type'] = self.fadeOutEdit.fadeType()
            conf['fadeout_duration'] = self.fadeOutEdit.duration()

        return conf
