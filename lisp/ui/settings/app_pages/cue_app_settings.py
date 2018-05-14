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

from PyQt5.QtCore import QT_TRANSLATE_NOOP, Qt
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox

from lisp.ui.settings.pages import ConfigurationPage
from lisp.ui.ui_utils import translate
from lisp.ui.widgets import FadeEdit


class CueAppSettings(ConfigurationPage):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'Cue Settings')

    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        # Interrupt
        self.interruptGroup = QGroupBox(self)
        self.interruptGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.interruptGroup)

        self.interruptFadeEdit = FadeEdit(self.interruptGroup)
        self.interruptGroup.layout().addWidget(self.interruptFadeEdit)

        # Action
        self.actionGroup = QGroupBox(self)
        self.actionGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.actionGroup)

        self.fadeActionEdit = FadeEdit(self.actionGroup)
        self.actionGroup.layout().addWidget(self.fadeActionEdit)

        self.retranslateUi()
        self.loadConfiguration()

    def retranslateUi(self):
        self.interruptGroup.setTitle(translate('CueSettings', 'Interrupt fade'))
        self.actionGroup.setTitle(translate('CueSettings', 'Fade actions'))

    def applySettings(self):
        self.config['cue.interruptFade'] = self.interruptFadeEdit.duration()
        self.config['cue.interruptFadeType'] = self.interruptFadeEdit.fadeType()
        self.config['cue.fadeAction'] = self.fadeActionEdit.duration()
        self.config['cue.fadeActionType'] = self.fadeActionEdit.fadeType()

        self.config.write()

    def loadConfiguration(self):
        self.interruptFadeEdit.setDuration(
            self.config.get('cue.interruptFade', 0))
        self.interruptFadeEdit.setFadeType(
            self.config.get('cue.interruptFadeType', ''))

        self.fadeActionEdit.setDuration(self.config.get('cue.fadeAction', 0))
        self.fadeActionEdit.setFadeType(
            self.config.get('cue.fadeActionType', ''))
