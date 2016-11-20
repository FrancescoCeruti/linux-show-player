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

from enum import Enum

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QGridLayout, QLabel, \
    QComboBox, QSpinBox, QFrame

from lisp.cues.cue import Cue, CueState
from lisp.ui.settings.cue_settings import CueSettingsRegistry,\
    SettingsPage


class OscMessageType(Enum):
    Int = 'Integer',
    Float = 'Float',
    Bool = 'Bool',
    String = 'String'


class OscCue(Cue):
    Name = QT_TRANSLATE_NOOP('CueName', 'OSC Cue')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @Cue.state.getter
    def state(self):
        return CueState.Stop

    def __start__(self):
        pass


class OscCueSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP('CueName', 'OSC Settings')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.msgGroup = QGroupBox(self)
        self.msgGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.msgGroup)

        self.retranslateUi()

    def retranslateUi(self):
        self.msgGroup.setTitle(translate('OscCue', 'OSC Message'))

    def get_settings(self):
        pass

    def load_settings(self, settings):
        pass

CueSettingsRegistry().add_item(OscCueSettings, OscCue)
