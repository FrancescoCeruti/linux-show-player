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
from lisp.ui.icons import icon_themes_names
from lisp.ui.settings.settings_page import ConfigurationPage
from lisp.ui.themes import themes_names
from lisp.ui.ui_utils import translate


class AppGeneral(ConfigurationPage):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'General')

    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        # Startup "layout"
        self.layoutGroup = QGroupBox(self)
        self.layoutGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.layoutGroup)

        self.startupDialogCheck = QCheckBox(self.layoutGroup)
        self.layoutGroup.layout().addWidget(self.startupDialogCheck)

        self.layoutCombo = QComboBox(self.layoutGroup)
        for layout in layouts.get_layouts():
            self.layoutCombo.addItem(layout.NAME, layout.__name__)
        self.layoutGroup.layout().addWidget(self.layoutCombo)

        self.startupDialogCheck.stateChanged.connect(
            self.layoutCombo.setDisabled)

        # Application theme
        self.themeGroup = QGroupBox(self)
        self.themeGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.themeGroup)

        self.themeLabel = QLabel(self.themeGroup)
        self.themeGroup.layout().addWidget(self.themeLabel, 0, 0)

        self.themeCombo = QComboBox(self.themeGroup)
        self.themeCombo.addItems(themes_names())
        self.themeGroup.layout().addWidget(self.themeCombo, 0, 1)

        self.iconsLabel = QLabel(self.themeGroup)
        self.themeGroup.layout().addWidget(self.iconsLabel, 1, 0)

        self.iconsCombo = QComboBox(self.themeGroup)
        self.iconsCombo.addItems(icon_themes_names())
        self.themeGroup.layout().addWidget(self.iconsCombo, 1, 1)

        self.retranslateUi()
        self.loadConfiguration()

    def retranslateUi(self):
        self.layoutGroup.setTitle(
            translate('AppGeneralSettings', 'Default layout'))
        self.startupDialogCheck.setText(
            translate('AppGeneralSettings', 'Enable startup layout selector'))
        self.themeGroup.setTitle(
            translate('AppGeneralSettings', 'Application themes'))
        self.themeLabel.setText(
            translate('AppGeneralSettings', 'UI theme'))
        self.iconsLabel.setText(
            translate('AppGeneralSettings', 'Icons theme'))

    def applySettings(self):
        if self.startupDialogCheck.isChecked():
            self.config['layout.default'] = 'NoDefault'
        else:
            self.config['layout.default'] = self.layoutCombo.currentData()

        self.config['theme.theme'] = self.themeCombo.currentText()
        self.config['theme.icons'] = self.iconsCombo.currentText()

        self.config.write()

    def loadConfiguration(self):
        layout_name = self.config.get('layout.default', 'nodefault')
        if layout_name.lower() == 'nodefault':
            self.startupDialogCheck.setChecked(True)
        else:
            self.layoutCombo.setCurrentText(layout_name)

        self.themeCombo.setCurrentText(self.config.get('theme.theme', ''))
        self.iconsCombo.setCurrentText(self.config.get('theme.icons', ''))