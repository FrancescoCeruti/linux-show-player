# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2018 Francesco Ceruti <ceppofrancy@gmail.com>
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
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QGridLayout, QCheckBox

from lisp.ui.settings.pages import ConfigurationPage
from lisp.ui.ui_utils import translate


class LayoutsSettings(ConfigurationPage):
    Name = 'Layouts'

    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.useFadeGroup = QGroupBox(self)
        self.useFadeGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.useFadeGroup)

        self.stopAllFade = QCheckBox(self.useFadeGroup)
        self.useFadeGroup.layout().addWidget(self.stopAllFade, 0, 1)

        self.pauseAllFade = QCheckBox(self.useFadeGroup)
        self.useFadeGroup.layout().addWidget(self.pauseAllFade, 1, 1)

        self.resumeAllFade = QCheckBox(self.useFadeGroup)
        self.useFadeGroup.layout().addWidget(self.resumeAllFade, 2, 1)

        self.interruptAllFade = QCheckBox(self.useFadeGroup)
        self.useFadeGroup.layout().addWidget(self.interruptAllFade, 3, 1)

        self.retranslateUi()
        self.loadSettings()

    def retranslateUi(self):
        self.useFadeGroup.setTitle(
            translate('ListLayout', 'Use fade (global actions)'))
        self.stopAllFade.setText(translate('ListLayout', 'Stop All'))
        self.pauseAllFade.setText(translate('ListLayout', 'Pause All'))
        self.resumeAllFade.setText(translate('ListLayout', 'Resume All'))
        self.interruptAllFade.setText(translate('ListLayout', 'Interrupt All'))

    def loadSettings(self):
        self.stopAllFade.setChecked(self.config['layout.stopAllFade'])
        self.pauseAllFade.setChecked(self.config['layout.pauseAllFade'])
        self.resumeAllFade.setChecked(self.config['layout.resumeAllFade'])
        self.interruptAllFade.setChecked(self.config['layout.interruptAllFade'])

    def applySettings(self):
        self.config['layout.stopAllFade'] = self.stopAllFade.isChecked()
        self.config['layout.pauseAllFade'] = self.pauseAllFade.isChecked()
        self.config['layout.resumeAllFade'] = self.resumeAllFade.isChecked()
        self.config['layout.interruptAllFade'] = self.interruptAllFade.isChecked()
        self.config.write()
