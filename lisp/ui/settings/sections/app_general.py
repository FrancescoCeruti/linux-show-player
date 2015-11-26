# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2015 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QCheckBox, QComboBox

from lisp import layouts
from lisp.ui import styles
from lisp.ui.settings.section import SettingsSection


class General(SettingsSection):

    NAME = 'General'

    def __init__(self, size, parent=None):
        super().__init__(size, parent)

        # Startup layout
        self.layoutGroup = QGroupBox(self)
        self.layoutGroup.setTitle('Startup layout')
        self.layoutGroup.setLayout(QVBoxLayout())
        self.layoutGroup.setGeometry(0, 0, self.width(), 120)

        self.startupDialogCheck = QCheckBox(self.layoutGroup)
        self.startupDialogCheck.setText('Use startup dialog')
        self.layoutGroup.layout().addWidget(self.startupDialogCheck)

        self.layoutCombo = QComboBox(self.layoutGroup)
        self.layoutCombo.addItems([lay.NAME for lay in layouts.get_layouts()])
        self.layoutGroup.layout().addWidget(self.layoutCombo)

        self.startupDialogCheck.clicked.connect(
            lambda check: self.layoutCombo.setEnabled(not check))

        # Application style
        self.themeGroup = QGroupBox(self)
        self.themeGroup.setTitle('Application theme')
        self.themeGroup.setLayout(QVBoxLayout())
        self.themeGroup.setGeometry(0, 125, self.width(), 80)

        self.themeCombo = QComboBox(self.themeGroup)
        self.themeCombo.addItems(styles.get_styles())
        self.themeGroup.layout().addWidget(self.themeCombo)

    def get_configuration(self):
        conf = {'Layout': {}, 'Theme': {}}

        if self.startupDialogCheck.isChecked():
            conf['Layout']['default'] = 'NoDefault'
        else:
            conf['Layout']['default'] = self.layoutCombo.currentText()

        conf['Theme']['theme'] = self.themeCombo.currentText()
        styles.apply_style(self.themeCombo.currentText())

        return conf

    def set_configuration(self, conf):
        if 'default' in conf['Layout']:
            if conf['Layout']['default'].lower() == 'nodefault':
                self.startupDialogCheck.setChecked(True)
                self.layoutCombo.setEnabled(False)
            else:
                self.layoutCombo.setCurrentText(conf['Layout']['default'])
        if 'theme' in conf['Theme']:
            self.themeCombo.setCurrentText(conf['Theme']['theme'])
