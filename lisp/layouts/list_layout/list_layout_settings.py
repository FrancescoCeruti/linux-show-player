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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QCheckBox

from lisp.ui.settings.settings_page import SettingsPage


class ListLayoutSettings(SettingsPage):

    NAME = 'List Layout'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.behaviorsGroup = QGroupBox(self)
        self.behaviorsGroup.setTitle('Default behaviors')
        self.behaviorsGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.behaviorsGroup)

        self.showPlaying = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.showPlaying)

        self.showDbMeters = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.showDbMeters)

        self.showAccurate = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.showAccurate)

        self.showSeek = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.showSeek)

        self.autoNext = QCheckBox(self.behaviorsGroup)
        self.behaviorsGroup.layout().addWidget(self.autoNext)

        self.retranslateUi()

    def retranslateUi(self):
        self.behaviorsGroup.setTitle('Default behaviors')
        self.showPlaying.setText('Show playing-sidebar')
        self.showDbMeters.setText('Show db-meters')
        self.showAccurate.setText('Show accurate time')
        self.showSeek.setText('Show seek sliders')
        self.autoNext.setText('Automatically select the next cue')

    def get_settings(self):
        conf = {}

        conf['showplaying'] = str(self.showPlaying.isChecked())
        conf['showdbmeters'] = str(self.showDbMeters.isChecked())
        conf['showseek'] = str(self.showSeek.isChecked())
        conf['showaccurate'] = str(self.showAccurate.isChecked())
        conf['autonext'] = str(self.autoNext.isChecked())

        return {'ListLayout': conf}

    def load_settings(self, settings):
        settings = settings.get('ListLayout', {})

        self.showPlaying.setChecked(settings.get('showplaying') == 'True')
        self.showDbMeters.setChecked(settings.get('showdbmeters') == 'True')
        self.showAccurate.setChecked(settings.get('showaccurate') == 'True')
        self.showSeek.setChecked(settings.get('showseek') == 'True')
        self.autoNext.setChecked(settings.get('autonext') == 'True')
