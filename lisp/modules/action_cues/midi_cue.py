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

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QGridLayout, QLabel, \
    QComboBox, QSpinBox, QFrame

from lisp.core.has_properties import Property
from lisp.cues.cue import Cue
from lisp.modules.midi.midi_output import MIDIOutput
from lisp.modules.midi.midi_utils import str_msg_to_dict, dict_msg_to_str
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.settings.settings_page import SettingsPage
from lisp.ui.ui_utils import translate


class MidiCue(Cue):
    Name = QT_TRANSLATE_NOOP('CueName', 'MIDI Cue')

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


class MidiCueSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'MIDI Settings')

    MSGS_ATTRIBUTES = {
        'note_on': ['channel', 'note', 'velocity'],
        'note_off': ['channel', 'note', 'velocity'],
        'control_change': ['channel', 'control', 'value'],
        'program_change': ['channel', 'program', None],
        'polytouch': ['channel', 'note', 'value'],
        'pitchwheel': ['channel', 'pitch', None],
        'song_select': ['song', None, None],
        'songpos': ['pos', None, None],
        'start': [None] * 3,
        'stop': [None] * 3,
        'continue': [None] * 3,
    }

    ATTRIBUTES_RANGE = {
        'channel': (1, 16, -1), 'note': (0, 127, 0),
        'velocity': (0, 127, 0), 'control': (0, 127, 0),
        'program': (0, 127, 0), 'value': (0, 127, 0),
        'song': (0, 127, 0), 'pitch': (-8192, 8191, 0),
        'pos': (0, 16383, 0)
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.msgGroup = QGroupBox(self)
        self.msgGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.msgGroup)

        # Message type
        self.msgTypeLabel = QLabel(self.msgGroup)
        self.msgGroup.layout().addWidget(self.msgTypeLabel, 0, 0)
        self.msgTypeCombo = QComboBox(self.msgGroup)
        self.msgTypeCombo.addItems(sorted(self.MSGS_ATTRIBUTES.keys()))
        self.msgTypeCombo.currentTextChanged.connect(self.__type_changed)
        self.msgGroup.layout().addWidget(self.msgTypeCombo, 0, 1)

        line = QFrame(self.msgGroup)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.msgGroup.layout().addWidget(line, 1, 0, 1, 2)

        # Data widgets
        self._data_widgets = []
        for n in range(2, 5):
            dataLabel = QLabel(self.msgGroup)
            dataSpin = QSpinBox(self.msgGroup)

            self.msgGroup.layout().addWidget(dataLabel, n, 0)
            self.msgGroup.layout().addWidget(dataSpin, n, 1)

            self._data_widgets.append((dataLabel, dataSpin))

        self.__type_changed(self.msgTypeCombo.currentText())

        self.retranslateUi()

    def retranslateUi(self):
        self.msgGroup.setTitle(translate('MIDICue', 'MIDI Message'))
        self.msgTypeLabel.setText(translate('MIDICue', 'Message type'))

    def __type_changed(self, msg_type):
        for label, spin, attr_name in self.__attributes(msg_type):
            if attr_name is None:
                label.setEnabled(False)
                label.setText('')
                spin.setEnabled(False)
            else:
                label.setEnabled(True)
                label.setText(attr_name.title())

                spin.setEnabled(True)
                spin.setRange(
                    *self.ATTRIBUTES_RANGE.get(attr_name, (0, 0, 0))[0:2])

    def get_settings(self):
        msg_type = self.msgTypeCombo.currentText()
        msg_dict = {'type': msg_type}

        for label, spin, attr_name in self.__attributes(msg_type):
            if spin.isEnabled():
                offset = self.ATTRIBUTES_RANGE.get(attr_name, (0, 0, 0))[2]
                msg_dict[attr_name] = spin.value() + offset

        return {'message': dict_msg_to_str(msg_dict)}

    def __attributes(self, msg_type):
        for (label, spin), attr in zip(self._data_widgets,
                                       self.MSGS_ATTRIBUTES[msg_type]):
            yield label, spin, attr

    def load_settings(self, settings):
        str_msg = settings.get('message', '')
        if str_msg:
            dict_msg = str_msg_to_dict(str_msg)
            self.msgTypeCombo.setCurrentText(dict_msg['type'])

            for label, spin, attr_name in self.__attributes(dict_msg['type']):
                offset = self.ATTRIBUTES_RANGE.get(attr_name, (0, 0, 0))[2]
                spin.setValue(dict_msg.get(label.text().lower(), 0) - offset)


CueSettingsRegistry().add_item(MidiCueSettings, MidiCue)
