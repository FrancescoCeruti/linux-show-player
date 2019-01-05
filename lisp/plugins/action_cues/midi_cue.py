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
from PyQt5.QtCore import QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import QVBoxLayout

from lisp.core.properties import Property
from lisp.cues.cue import Cue
from lisp.plugins import get_plugin
from lisp.plugins.midi.midi_utils import str_msg_to_dict, dict_msg_to_str
from lisp.plugins.midi.widgets import MIDIMessageEdit
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)


class MidiCue(Cue):
    Name = QT_TRANSLATE_NOOP("CueName", "MIDI Cue")

    message = Property(default="")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = translate("CueName", self.Name)
        self.__midi = get_plugin("Midi")

    def __start__(self, fade=False):
        if self.message:
            self.__midi.output.send_from_str(self.message)

        return False


class MidiCueSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "MIDI Settings")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.midiEdit = MIDIMessageEdit(parent=self)
        self.layout().addWidget(self.midiEdit)

    def getSettings(self):
        return {"message": dict_msg_to_str(self.midiEdit.getMessageDict())}

    def loadSettings(self, settings):
        message = settings.get("message", "")
        if message:
            self.midiEdit.setMessageDict(str_msg_to_dict(message))


CueSettingsRegistry().add(MidiCueSettings, MidiCue)
