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

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QCheckBox, QComboBox, \
    QGridLayout, QLabel

from lisp import layouts
from lisp.ui.settings.settings_page import SettingsPage
from lisp.ui.themes import THEMES, ICON_THEMES
from lisp.ui.ui_utils import translate


class AppGeneral(SettingsPage):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'General')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        # Startup layout
        self.layoutGroup = QGroupBox(self)
        self.layoutGroup.setTitle(
            translate('AppGeneralSettings', 'Startup layout'))
        self.layoutGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.layoutGroup)

        self.startupDialogCheck = QCheckBox(self.layoutGroup)
        self.startupDialogCheck.setText(
            translate('AppGeneralSettings', 'Use startup dialog'))
        self.layoutGroup.layout().addWidget(self.startupDialogCheck)

        self.layoutCombo = QComboBox(self.layoutGroup)
        self.layoutCombo.addItems([lay.NAME for lay in layouts.get_layouts()])
        self.layoutGroup.layout().addWidget(self.layoutCombo)

        self.startupDialogCheck.clicked.connect(
            lambda check: self.layoutCombo.setEnabled(not check))

        # Application style
        self.themeGroup = QGroupBox(self)
        self.themeGroup.setTitle(
            translate('AppGeneralSettings', 'Application theme'))
        self.themeGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.themeGroup)

        self.themeLabel = QLabel(self.themeGroup)
        self.themeLabel.setText(
            translate('AppGeneralSettings', 'Theme'))
        self.themeGroup.layout().addWidget(self.themeLabel, 0, 0)

        self.themeCombo = QComboBox(self.themeGroup)
        self.themeCombo.addItems(THEMES.keys())
        self.themeGroup.layout().addWidget(self.themeCombo, 0, 1)

        self.iconsLabel = QLabel(self.themeGroup)
        self.iconsLabel.setText(
            translate('AppGeneralSettings', 'Icons'))
        self.themeGroup.layout().addWidget(self.iconsLabel, 1, 0)

        self.iconsCombo = QComboBox(self.themeGroup)
        self.iconsCombo.addItems(ICON_THEMES.keys())
        self.themeGroup.layout().addWidget(self.iconsCombo, 1, 1)

    def get_settings(self):
        conf = {'layout': {}, 'theme': {}}

        if self.startupDialogCheck.isChecked():
            conf['layout']['default'] = 'NoDefault'
        else:
            conf['layout']['default'] = self.layoutCombo.currentText()

        conf['theme']['theme'] = self.themeCombo.currentText()
        conf['theme']['icons'] = self.iconsCombo.currentText()

        return conf

    def load_settings(self, settings):
        if settings['layout']['default'].lower() == 'nodefault':
            self.startupDialogCheck.setChecked(True)
            self.layoutCombo.setEnabled(False)
        else:
            self.layoutCombo.setCurrentText(settings['layout']['default'])

        self.themeCombo.setCurrentText(settings['theme']['theme'])
        self.iconsCombo.setCurrentText(settings['theme']['icons'])
