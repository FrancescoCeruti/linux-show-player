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

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QDoubleSpinBox
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QCheckBox, QComboBox, \
    QHBoxLayout, QLabel, QKeySequenceEdit, QGridLayout

from lisp.ui.settings.settings_page import SettingsPage
from lisp.ui.ui_utils import translate
from lisp.ui.widgets import FadeComboBox


class ListLayoutSettings(SettingsPage):
    Name = 'List Layout'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.behaviorsGroup = QGroupBox(self)
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

        self.endListLayout = QHBoxLayout()
        self.behaviorsGroup.layout().addLayout(self.endListLayout)
        self.endListLabel = QLabel(self.behaviorsGroup)
        self.endListLayout.addWidget(self.endListLabel)
        self.endListBehavior = QComboBox(self.behaviorsGroup)
        self.endListBehavior.addItem(translate('ListLayout', 'Stop'), 'Stop')
        self.endListBehavior.addItem(translate('ListLayout', 'Restart'),
                                     'Restart')
        self.endListLayout.addWidget(self.endListBehavior)
        self.endListLayout.setStretch(0, 2)
        self.endListLayout.setStretch(1, 5)

        self.goKeyLayout = QHBoxLayout()
        self.behaviorsGroup.layout().addLayout(self.goKeyLayout)
        self.goKeyLabel = QLabel(self.behaviorsGroup)
        self.goKeyLayout.addWidget(self.goKeyLabel)
        self.goKeyEdit = QKeySequenceEdit(self.behaviorsGroup)
        self.goKeyLayout.addWidget(self.goKeyEdit)
        self.goKeyLayout.setStretch(0, 2)
        self.goKeyLayout.setStretch(1, 5)

        self.useFadeGroup = QGroupBox(self)
        self.useFadeGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.useFadeGroup)

        # per-cue
        self.stopCueFade = QCheckBox(self.useFadeGroup)
        self.useFadeGroup.layout().addWidget(self.stopCueFade, 0, 0)
        self.pauseCueFade = QCheckBox(self.useFadeGroup)
        self.useFadeGroup.layout().addWidget(self.pauseCueFade, 1, 0)
        self.resumeCueFade = QCheckBox(self.useFadeGroup)
        self.useFadeGroup.layout().addWidget(self.resumeCueFade, 2, 0)
        self.interruptCueFade = QCheckBox(self.useFadeGroup)
        self.useFadeGroup.layout().addWidget(self.interruptCueFade, 3, 0)

        # all
        self.stopAllFade = QCheckBox(self.useFadeGroup)
        self.useFadeGroup.layout().addWidget(self.stopAllFade, 0, 1)
        self.pauseAllFade = QCheckBox(self.useFadeGroup)
        self.useFadeGroup.layout().addWidget(self.pauseAllFade, 1, 1)
        self.resumeAllFade = QCheckBox(self.useFadeGroup)
        self.useFadeGroup.layout().addWidget(self.resumeAllFade, 2, 1)
        self.interruptAllFade = QCheckBox(self.useFadeGroup)
        self.useFadeGroup.layout().addWidget(self.interruptAllFade, 3, 1)

        self.retranslateUi()

    def retranslateUi(self):
        self.behaviorsGroup.setTitle(
            translate('ListLayout', 'Default behaviors'))
        self.showPlaying.setText(translate('ListLayout', 'Show playing cues'))
        self.showDbMeters.setText(translate('ListLayout', 'Show dB-meters'))
        self.showAccurate.setText(translate('ListLayout', 'Show accurate time'))
        self.showSeek.setText(translate('ListLayout', 'Show seek-bars'))
        self.autoNext.setText(translate('ListLayout', 'Auto-select next cue'))
        self.endListLabel.setText(translate('ListLayout', 'At list end:'))
        self.goKeyLabel.setText(translate('ListLayout', 'Go key:'))

        self.useFadeGroup.setTitle(translate('ListLayout', 'Use fade'))
        self.stopCueFade.setText(translate('ListLayout', 'Stop Cue'))
        self.pauseCueFade.setText(translate('ListLayout', 'Pause Cue'))
        self.resumeCueFade.setText(translate('ListLayout', 'Resume Cue'))
        self.interruptCueFade.setText(translate('ListLayout', 'Interrupt Cue'))
        self.stopAllFade.setText(translate('ListLayout', 'Stop All'))
        self.pauseAllFade.setText(translate('ListLayout', 'Pause All'))
        self.resumeAllFade.setText(translate('ListLayout', 'Resume All'))
        self.interruptAllFade.setText(translate('ListLayout', 'Interrupt All'))

    def get_settings(self):
        settings = {
            'showplaying': str(self.showPlaying.isChecked()),
            'showdbmeters': str(self.showDbMeters.isChecked()),
            'showseek': str(self.showSeek.isChecked()),
            'showaccurate': str(self.showAccurate.isChecked()),
            'autocontinue': str(self.autoNext.isChecked()),
            'endlist': str(self.endListBehavior.currentData()),
            'gokey': self.goKeyEdit.keySequence().toString(
                QKeySequence.NativeText),
            'stopcuefade': str(self.stopCueFade.isChecked()),
            'pausecuefade': str(self.pauseCueFade.isChecked()),
            'resumecuefade': str(self.resumeCueFade.isChecked()),
            'interruptcuefade': str(self.interruptCueFade.isChecked()),
            'stopallfade': str(self.stopAllFade.isChecked()),
            'pauseallfade': str(self.pauseAllFade.isChecked()),
            'resumeallfade': str(self.resumeAllFade.isChecked()),
            'interruptallfade': str(self.interruptAllFade.isChecked()),
        }

        return {'ListLayout': settings}

    def load_settings(self, settings):
        settings = settings.get('ListLayout', {})

        self.showPlaying.setChecked(settings.get('showplaying') == 'True')
        self.showDbMeters.setChecked(settings.get('showdbmeters') == 'True')
        self.showAccurate.setChecked(settings.get('showaccurate') == 'True')
        self.showSeek.setChecked(settings.get('showseek') == 'True')
        self.autoNext.setChecked(settings.get('autocontinue') == 'True')
        self.endListBehavior.setCurrentText(
            translate('ListLayout', settings.get('endlist', '')))
        self.goKeyEdit.setKeySequence(
            QKeySequence(settings.get('gokey', 'Space'),
                         QKeySequence.NativeText))

        self.stopCueFade.setChecked(settings.get('stopcuefade') == 'True')
        self.pauseCueFade.setChecked(settings.get('pausecuefade') == 'True')
        self.resumeCueFade.setChecked(settings.get('resumecuefade') == 'True')
        self.interruptCueFade.setChecked(
            settings.get('interruptcuefade') == 'True')

        self.stopAllFade.setChecked(settings.get('stopallfade') == 'True')
        self.pauseAllFade.setChecked(settings.get('pauseallfade') == 'True')
        self.resumeAllFade.setChecked(settings.get('resumeallfade') == 'True')
        self.interruptAllFade.setChecked(
            settings.get('interruptallfade') == 'True')