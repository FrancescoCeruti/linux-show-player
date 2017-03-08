# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2017 Francesco Ceruti <ceppofrancy@gmail.com>
# Copyright 2017 Thomas Achtner <info@offtools.de>
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

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import QVBoxLayout, QPushButton

from lisp.core.has_properties import Property
from lisp.cues.cue import Cue
from lisp.modules.midi.midi_msc import MscArgument, MscStringParser
from lisp.modules.midi.midi_output import MIDIOutput
from lisp.ui import elogging
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.settings.settings_page import SettingsPage
from lisp.ui.widgets.msc_groupbox import MscGroupBox
from lisp.ui.ui_utils import translate


class MscCue(Cue):
    Name = QT_TRANSLATE_NOOP('CueName', 'MSC Cue')

    message = Property(default='')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = translate('CueName', self.Name)

        midi_out = MIDIOutput()
        if not midi_out.is_open():
            midi_out.open()

    def __start__(self, fade=False):
        if self.message:
            MIDIOutput().send_from_str(self.message)

        return False


class MscCueSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'MSC Settings')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.mscGroup = MscGroupBox(self)
        self.layout().addWidget(self.mscGroup)

        self.testButton = QPushButton(self.mscGroup)
        self.testButton.pressed.connect(self.__test_message)
        self.testButton.setText(translate('MSCCue', 'Test'))
        self.mscGroup.layout().addWidget(self.testButton, 13, 2)

    def __test_message(self):
        message = self.mscGroup.get_message()
        MIDIOutput().send_from_str(message.message_str)

    def get_settings(self):

        message = self.mscGroup.get_message()
        msg_str = message.message_str
        if not msg_str:
            elogging.error("MscCue: could not create MSC messsage")

        elogging.debug("MscCue: message string: {0}".format(msg_str))
        return {'message': msg_str}

    def load_settings(self, settings):
        msg_str = settings.get('message', '')

        if not msg_str:
            return

        parser = MscStringParser(msg_str)

        if not parser.valid:
            elogging.error("MscCue: could not parse MSC message")
            return

        self.mscGroup.device_id = parser.device_id
        self.mscGroup.command_format = parser.command_format
        self.mscGroup.command = parser.command

        for msc_arg in MscArgument:
            value = parser.get(msc_arg)
            if value is not None:
                if msc_arg is MscArgument.TIME_TYPE:
                    pass
                elif msc_arg is MscArgument.TIMECODE:
                    self.mscGroup.set_argument(MscArgument.TIME_TYPE, parser[MscArgument.TIME_TYPE])
                    self.mscGroup.set_argument(MscArgument.TIMECODE, value)
                    self.mscGroup.checkbox_toggle(msc_arg, True)
                    self.mscGroup.checkbox_enable(msc_arg, not parser.required(msc_arg))

                else:
                    self.mscGroup.set_argument(msc_arg, value)
                    self.mscGroup.checkbox_toggle(msc_arg, True)
                    self.mscGroup.checkbox_enable(msc_arg, not parser.required(msc_arg))
            else:
                self.mscGroup.checkbox_toggle(msc_arg, False)

CueSettingsRegistry().add_item(MscCueSettings, MscCue)
