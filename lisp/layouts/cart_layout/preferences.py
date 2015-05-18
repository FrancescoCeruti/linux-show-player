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

from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QCheckBox, QGridLayout, \
    QSpinBox, QLabel

from lisp.ui.settings.section import SettingsSection


class CartLayoutPreferences(SettingsSection):

    NAME = 'Cart Layout'

    def __init__(self, size, parent=None):
        super().__init__(size, parent)

        self.behaviorsGroup = QGroupBox(self)
        self.behaviorsGroup.setLayout(QVBoxLayout())
        self.behaviorsGroup.setGeometry(0, 0, self.width(), 140)

        self.countdownMode = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.countdownMode)

        self.showSeek = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.showSeek)

        self.showDbMeters = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.showDbMeters)

        self.showAccurate = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.showAccurate)

        self.autoAddPage = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.autoAddPage)

        self.gridSizeGroup = QGroupBox(self)
        self.gridSizeGroup.setTitle('Grid size')
        self.gridSizeGroup.setLayout(QGridLayout())
        self.gridSizeGroup.setGeometry(0, 145, self.width(), 120)

        self.columnsSpin = QSpinBox(self.gridSizeGroup)
        self.columnsSpin.setRange(1, 16)
        self.gridSizeGroup.layout().addWidget(self.columnsSpin, 0, 0)

        self.columnsLabel = QLabel(self.gridSizeGroup)
        self.gridSizeGroup.layout().addWidget(self.columnsLabel, 0, 1)

        self.rowsSpin = QSpinBox(self.gridSizeGroup)
        self.rowsSpin.setRange(1, 16)
        self.gridSizeGroup.layout().addWidget(self.rowsSpin, 1, 0)

        self.rowsLabel = QLabel(self.gridSizeGroup)
        self.gridSizeGroup.layout().addWidget(self.rowsLabel, 1, 1)

        self.gridSizeGroup.layout().setColumnStretch(0, 5)
        self.gridSizeGroup.layout().setColumnStretch(1, 3)

        self.retranslateUi()

    def retranslateUi(self):
        self.behaviorsGroup.setTitle('Default behaviors')
        self.countdownMode.setText('Countdown mode')
        self.showSeek.setText('Show seek sliders')
        self.showDbMeters.setText('Show db-meters')
        self.showAccurate.setText('Show accurate time')
        self.autoAddPage.setText('Automatically add new page')
        self.columnsLabel.setText('Number of columns')
        self.rowsLabel.setText('Number of rows')

    def get_configuration(self):
        conf = {}

        conf['gridcolumns'] = str(self.columnsSpin.value())
        conf['gridrows'] = str(self.rowsSpin.value())
        conf['showdbmeters'] = str(self.showDbMeters.isChecked())
        conf['showseek'] = str(self.showSeek.isChecked())
        conf['showaccurate'] = str(self.showAccurate.isChecked())
        conf['countdown'] = str(self.countdownMode.isChecked())
        conf['autoaddpage'] = str(self.autoAddPage.isChecked())

        return {'CartLayout': conf}

    def set_configuration(self, conf):
        if 'CartLayout' in conf:
            conf = conf['CartLayout']
            if 'gridcolumns' in conf:
                self.columnsSpin.setValue(int(conf['gridcolumns']))
            if 'gridrows' in conf:
                self.rowsSpin.setValue(int(conf['gridrows']))
            if 'showsseek' in conf:
                self.showSeek.setChecked(conf['showseek'] == 'True')
            if 'showdbmeter' in conf:
                self.showDbMeters.setChecked(conf['showdbmeters'] == 'True')
            if 'showaccurate' in conf:
                self.showAccurate.setChecked(conf['showaccurate'] == 'True')
            if 'countdown' in conf:
                self.countdownMode.setChecked(conf['countdown'] == 'True')
            if 'autoaddpage' in conf:
                self.autoAddPage.setChecked(conf['autoaddpage'] == 'True')
