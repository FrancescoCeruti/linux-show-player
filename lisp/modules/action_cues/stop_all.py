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

from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QHBoxLayout, QCheckBox

from lisp.application import Application
from lisp.core.decorators import async
from lisp.core.has_properties import Property
from lisp.cues.media_cue import MediaCue
from lisp.layouts.cue_layout import CueLayout
from lisp.ui.settings.section import SettingsSection
from lisp.cues.cue import Cue


class StopAll(Cue):

    Name = 'Stop-All'

    pause_mode = Property(default=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = self.Name

    @async
    def execute(self, action=Cue.CueAction.Default):
        self.on_execute.emit(self, action)

        if self.pause_mode:
            cue_action = MediaCue.CueAction.Pause
        else:
            cue_action = MediaCue.CueAction.Stop

        layout = Application().layout
        for cue in layout.get_cues(cue_class=MediaCue):
            cue.execute(action=cue_action)

        self.executed.emit(self, action)


class StopAllSettings(SettingsSection):

    Name = 'Cue Settings'

    def __init__(self, size, cue=None, parent=None):
        super().__init__(size, cue=cue, parent=parent)

        self.setLayout(QVBoxLayout(self))

        self.group = QGroupBox(self)
        self.group.setTitle('Mode')
        self.group.setLayout(QHBoxLayout(self.group))

        self.pauseMode = QCheckBox(self.group)
        self.pauseMode.setText('Pause mode')
        self.group.layout().addWidget(self.pauseMode)

        self.layout().addWidget(self.group)
        self.layout().addSpacing(self.height() - 100)

    def enable_check(self, enable):
        self.group.setCheckable(enable)
        self.group.setChecked(False)

    def get_configuration(self):
        conf = {}

        if not (self.group.isCheckable() and not self.group.isChecked()):
            conf['pause_mode'] = self.pauseMode.isChecked()

        return conf

    def set_configuration(self, conf):
        if 'pause_mode' in conf:
            self.pauseMode.setChecked(conf['pause_mode'])

CueLayout.add_settings_section(StopAllSettings, StopAll)
