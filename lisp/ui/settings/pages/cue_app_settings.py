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

from lisp.ui.settings.settings_page import SettingsPage
from lisp.ui.ui_utils import translate
from lisp.ui.widgets.fade_edit import FadeEdit


class CueAppSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'Cue Settings')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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

    def retranslateUi(self):
        self.interruptGroup.setTitle(translate('CueSettings', 'Interrupt Fade'))
        self.actionGroup.setTitle(translate('CueSettings', 'Fade Action'))

    def load_settings(self, settings):
        # Interrupt
        self.interruptFadeEdit.setDuration(
            float(settings['Cue'].get('interruptfade', 0)))
        self.interruptFadeEdit.setFadeType(
            settings['Cue'].get('interruptfadetype', ''))

        # FadeAction
        self.fadeActionEdit.setDuration(
            float(settings['Cue'].get('fadeactionduration', 0)))
        self.fadeActionEdit.setFadeType(
            settings['Cue'].get('fadeactiontype', ''))

    def get_settings(self):
        return {'Cue': {
            'interruptfade': str(self.interruptFadeEdit.duration()),
            'interruptfadetype': self.interruptFadeEdit.fadeType(),
            'fadeactionduration': str(self.fadeActionEdit.duration()),
            'fadeactiontype': self.fadeActionEdit.fadeType()
        }}
