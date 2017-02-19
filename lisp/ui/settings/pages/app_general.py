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
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QCheckBox, QComboBox

from lisp import layouts
from lisp.ui.styles import styles
from lisp.ui.settings.settings_page import SettingsPage
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
        self.themeGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.themeGroup)

        self.themeCombo = QComboBox(self.themeGroup)
        self.themeCombo.addItems(styles.styles())
        self.themeGroup.layout().addWidget(self.themeCombo)

    def get_settings(self):
        conf = {'Layout': {}, 'Theme': {}}

        if self.startupDialogCheck.isChecked():
            conf['Layout']['default'] = 'NoDefault'
        else:
            conf['Layout']['default'] = self.layoutCombo.currentText()

        conf['Theme']['theme'] = self.themeCombo.currentText()
        styles.apply_style(self.themeCombo.currentText())

        return conf

    def load_settings(self, settings):
        if 'default' in settings['Layout']:
            if settings['Layout']['default'].lower() == 'nodefault':
                self.startupDialogCheck.setChecked(True)
                self.layoutCombo.setEnabled(False)
            else:
                self.layoutCombo.setCurrentText(settings['Layout']['default'])
        if 'theme' in settings['Theme']:
            self.themeCombo.setCurrentText(settings['Theme']['theme'])
