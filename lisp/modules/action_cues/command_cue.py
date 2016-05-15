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

import subprocess

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QLineEdit, QCheckBox

from lisp.core.decorators import async
from lisp.core.has_properties import Property
from lisp.cues.cue import Cue, CueState, CueAction
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.settings.settings_page import SettingsPage


class CommandCue(Cue):
    """Cue able to execute system commands.

    Implemented using :class:`subprocess.Popen` with *shell=True*
    """

    Name = 'Command Cue'
    CueActions = (CueAction.Start, CueAction.Stop, CueAction.Default)

    command = Property(default='')
    no_output = Property(default=True)
    kill = Property(default=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = self.Name

        self.__state = CueState.Stop
        self.__process = None

    @Cue.state.getter
    def state(self):
        return self.__state

    @async
    def __start__(self):
        if not self.command.strip():
            return

        if self.__state == CueState.Stop or self.__state == CueState.Error:
            self.__state = CueState.Running
            self.started.emit(self)

            # If no_output is True, "suppress" all the outputs
            std = subprocess.DEVNULL if self.no_output else None
            # Execute the command
            self.__process = subprocess.Popen(self.command, shell=True,
                                              stdout=std, stderr=std)
            rcode = self.__process.wait()

            if rcode == 0 or rcode == -9:
                # If terminate normally or killed, set the cue as ended
                self.__state = CueState.Stop
                self.end.emit(self)
            else:
                self.__state = CueState.Error
                self.error.emit(self, 'Process exited with an error status',
                                'Exit code: {}'.format(rcode))

    def __stop__(self):
        if self.__state == CueState.Running:
            if self.kill:
                self.__process.kill()
            else:
                self.__process.terminate()

            self.__state = CueState.Stop
            self.stopped.emit(self)


class CommandCueSettings(SettingsPage):
    Name = 'Command Cue'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.group = QGroupBox(self)
        self.group.setTitle('Command')
        self.group.setLayout(QVBoxLayout(self.group))
        self.layout().addWidget(self.group)

        self.commandLineEdit = QLineEdit(self.group)
        self.commandLineEdit.setPlaceholderText(
            'Command to execute as in a shell')
        self.group.layout().addWidget(self.commandLineEdit)

        self.noOutputCheckBox = QCheckBox(self)
        self.noOutputCheckBox.setText('Discard command output')
        self.layout().addWidget(self.noOutputCheckBox)

        self.killCheckBox = QCheckBox(self)
        self.killCheckBox.setText('Kill instead of terminate')
        self.layout().addWidget(self.killCheckBox)

    def enable_check(self, enabled):
        self.group.setCheckable(enabled)
        self.group.setChecked(False)

        self.noOutputCheckBox.setTristate(enabled)
        if enabled:
            self.noOutputCheckBox.setCheckState(Qt.PartiallyChecked)

        self.killCheckBox.setTristate(enabled)
        if enabled:
            self.killCheckBox.setCheckState(Qt.PartiallyChecked)

    def load_settings(self, settings):
        self.commandLineEdit.setText(settings.get('command', ''))
        self.noOutputCheckBox.setChecked(settings.get('no_output', True))
        self.killCheckBox.setChecked(settings.get('kill', False))

    def get_settings(self):
        settings = {}

        if not (self.group.isCheckable() and not self.group.isChecked()):
            if self.commandLineEdit.text().strip():
                settings['command'] = self.commandLineEdit.text()
        if self.noOutputCheckBox.checkState() != Qt.PartiallyChecked:
            settings['no_output'] = self.noOutputCheckBox.isChecked()
        if self.killCheckBox.checkState() != Qt.PartiallyChecked:
            settings['kill'] = self.killCheckBox.isChecked()

        return settings


CueSettingsRegistry().add_item(CommandCueSettings, CommandCue)
