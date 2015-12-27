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

from PyQt5 import QtCore
from PyQt5.QtCore import QTime
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QPushButton, QLabel, \
    QHBoxLayout, QTimeEdit

from lisp.application import Application
from lisp.core.has_properties import Property
from lisp.cues.cue import Cue, CueState
from lisp.cues.media_cue import MediaCue
from lisp.layouts.cue_layout import CueLayout
from lisp.ui.cuelistdialog import CueListDialog
from lisp.ui.settings.section import SettingsSection


class SeekAction(Cue):
    Name = 'Seek Action'

    target_id = Property()
    time = Property(default=-1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = self.Name

    @Cue.state.getter
    def state(self):
        return CueState.Stop

    def __start__(self):
        cue = Application().cue_model.get(self.target_id)
        if isinstance(cue, MediaCue) and self.time >= 0:
            cue.media.seek(self.time)


class SeekSettings(SettingsSection):
    Name = 'Seek Settings'

    def __init__(self, size, cue=None, parent=None):
        super().__init__(size, cue=cue, parent=parent)

        self.cue_id = -1
        self.setLayout(QVBoxLayout(self))

        self.cueDialog = CueListDialog(
            cues=Application().cue_model.filter(MediaCue), parent=self)

        self.cueGroup = QGroupBox(self)
        self.cueGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.cueGroup)

        self.cueButton = QPushButton(self.cueGroup)
        self.cueButton.clicked.connect(self.select_cue)
        self.cueGroup.layout().addWidget(self.cueButton)

        self.cueLabel = QLabel(self.cueGroup)
        self.cueLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.cueGroup.layout().addWidget(self.cueLabel)

        self.seekGroup = QGroupBox(self)
        self.seekGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.seekGroup)

        self.seekEdit = QTimeEdit(self.seekGroup)
        self.seekEdit.setDisplayFormat('HH.mm.ss.zzz')
        self.seekGroup.layout().addWidget(self.seekEdit)

        self.seekLabel = QLabel(self.seekGroup)
        self.seekLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.seekGroup.layout().addWidget(self.seekLabel)

        self.layout().addSpacing(200)

        self.retranslateUi()

    def retranslateUi(self):
        self.cueGroup.setTitle('Cue')
        self.cueButton.setText('Click to select')
        self.cueLabel.setText('Not selected')
        self.seekGroup.setTitle('Seek')
        self.seekLabel.setText('Time to reach')

    def select_cue(self):
        if self.cueDialog.exec_() == self.cueDialog.Accepted:
            cue = self.cueDialog.selected_cues()[0]

            self.cue_id = cue.id
            self.seekEdit.setMaximumTime(
                QTime.fromMSecsSinceStartOfDay(cue.media.duration))
            self.cueLabel.setText(cue.name)

    def enable_check(self, enable):
        self.cueGroup.setCheckable(enable)
        self.cueGroup.setChecked(False)

        self.seekGroup.setCheckable(enable)
        self.seekGroup.setChecked(False)

    def get_configuration(self):
        return {'target_id': self.cue_id,
                'time': self.seekEdit.time().msecsSinceStartOfDay()}

    def set_configuration(self, conf):
        if conf is not None:
            cue = Application().cue_model.get(conf['target_id'])
            if cue is not None:
                self.cue_id = conf['target_id']
                self.seekEdit.setTime(
                    QTime.fromMSecsSinceStartOfDay(conf['time']))
                self.seekEdit.setMaximumTime(
                    QTime.fromMSecsSinceStartOfDay(cue.media.duration))
                self.cueLabel.setText(cue.name)


CueLayout.add_settings_section(SeekSettings, SeekAction)
