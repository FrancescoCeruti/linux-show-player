##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5.QtWidgets import *  # @UnusedWildImport
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

        conf['Theme']['current'] = self.themeCombo.currentText()
        styles.apply_style(self.themeCombo.currentText())

        return conf

    def set_configuration(self, conf):
        if 'default' in conf['Layout']:
            if conf['Layout']['default'].lower() == 'nodefault':
                self.startupDialogCheck.setChecked(True)
                self.layoutCombo.setEnabled(False)
            else:
                self.layoutCombo.setCurrentText(conf['Layout']['default'])
        if 'current' in conf['Theme']:
            self.themeCombo.setCurrentText(conf['Theme']['current'])
