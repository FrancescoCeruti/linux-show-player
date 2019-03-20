# This file is part of Linux Show Player
#
# Copyright 2018 Francesco Ceruti <ceppofrancy@gmail.com>
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

import logging
import subprocess

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QLineEdit, QCheckBox

from lisp.core.decorators import async_function
from lisp.core.properties import Property
from lisp.cues.cue import Cue, CueAction
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)


class CommandCue(Cue):
    """Cue able to execute system commands.

    Implemented using :class:`subprocess.Popen` with *shell=True*
    """

    Name = QT_TRANSLATE_NOOP("CueName", "Command Cue")
    Category = None
    CueActions = (CueAction.Default, CueAction.Start, CueAction.Stop)

    command = Property(default="")
    no_output = Property(default=True)
    no_error = Property(default=True)
    kill = Property(default=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = translate("CueName", self.Name)

        self.__process = None
        self.__stopped = False

    def __start__(self, fade=False):
        self.__exec_command()
        return True

    @async_function
    def __exec_command(self):
        if not self.command.strip():
            return

        # If no_output is True, discard all the outputs
        std = subprocess.DEVNULL if self.no_output else None
        # Execute the command
        self.__process = subprocess.Popen(
            self.command, shell=True, stdout=std, stderr=std
        )
        rcode = self.__process.wait()

        if rcode == 0 or rcode == -9 or self.no_error:
            # If terminate normally, killed or in no-error mode
            if not self.__stopped:
                self._ended()
        elif not self.no_error:
            # If an error occurs and not in no-error mode
            logger.error(
                translate(
                    "CommandCue",
                    "Command cue ended with an error status. Exit code: {}",
                ).format(rcode)
            )
            self._error()

        self.__process = None
        self.__stopped = False

    def __stop__(self, fade=False):
        if self.__process is not None:
            self.__stopped = True
            if self.kill:
                self.__process.kill()
            else:
                self.__process.terminate()

        return True

    __interrupt__ = __stop__


class CommandCueSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "Command")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.group = QGroupBox(self)
        self.group.setLayout(QVBoxLayout(self.group))
        self.layout().addWidget(self.group)

        self.commandLineEdit = QLineEdit(self.group)
        self.group.layout().addWidget(self.commandLineEdit)

        self.noOutputCheckBox = QCheckBox(self)
        self.layout().addWidget(self.noOutputCheckBox)

        self.noErrorCheckBox = QCheckBox(self)
        self.layout().addWidget(self.noErrorCheckBox)

        self.killCheckBox = QCheckBox(self)
        self.layout().addWidget(self.killCheckBox)

        self.retranslateUi()

    def retranslateUi(self):
        self.group.setTitle(translate("CommandCue", "Command"))
        self.commandLineEdit.setPlaceholderText(
            translate("CommandCue", "Command to execute, as in a shell")
        )
        self.noOutputCheckBox.setText(
            translate("CommandCue", "Discard command output")
        )
        self.noErrorCheckBox.setText(
            translate("CommandCue", "Ignore command errors")
        )
        self.killCheckBox.setText(
            translate("CommandCue", "Kill instead of terminate")
        )

    def enableCheck(self, enabled):
        self.group.setCheckable(enabled)
        self.group.setChecked(False)

        self.noOutputCheckBox.setTristate(enabled)
        if enabled:
            self.noOutputCheckBox.setCheckState(Qt.PartiallyChecked)

        self.noErrorCheckBox.setTristate(enabled)
        if enabled:
            self.killCheckBox.setCheckState(Qt.PartiallyChecked)

        self.killCheckBox.setTristate(enabled)
        if enabled:
            self.killCheckBox.setCheckState(Qt.PartiallyChecked)

    def loadSettings(self, settings):
        self.commandLineEdit.setText(settings.get("command", ""))
        self.noOutputCheckBox.setChecked(settings.get("no_output", True))
        self.noErrorCheckBox.setChecked(settings.get("no_error", True))
        self.killCheckBox.setChecked(settings.get("kill", False))

    def getSettings(self):
        settings = {}

        if not (self.group.isCheckable() and not self.group.isChecked()):
            if self.commandLineEdit.text().strip():
                settings["command"] = self.commandLineEdit.text()
        if self.noOutputCheckBox.checkState() != Qt.PartiallyChecked:
            settings["no_output"] = self.noOutputCheckBox.isChecked()
        if self.noErrorCheckBox.checkState() != Qt.PartiallyChecked:
            settings["no_error"] = self.noErrorCheckBox.isChecked()
        if self.killCheckBox.checkState() != Qt.PartiallyChecked:
            settings["kill"] = self.killCheckBox.isChecked()

        return settings


CueSettingsRegistry().add(CommandCueSettings, CommandCue)
