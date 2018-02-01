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
from lisp.modules.midi.midi_utils import str_msg_to_dict, dict_msg_to_str, \
    MIDI_ATTRIBUTES, MIDI_MESSAGES
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
    OFFSETS = {'channel': 1}

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
        self.msgTypeCombo.addItems(sorted(MIDI_MESSAGES.keys()))
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
        for label, spin in self._data_widgets:
            label.setEnabled(False)
            label.setText('')
            spin.setEnabled(False)

        for label, spin, attr_name in self.__attributes(msg_type):
            label.setEnabled(True)
            label.setText(attr_name.title())

            spin.setEnabled(True)

            min_, max_, def_ = MIDI_ATTRIBUTES.get(attr_name, (0, 0, 0))
            # Add an offset for displaying purposes
            off = MidiCueSettings.OFFSETS.get(attr_name, 0)
            spin.setRange(min_ + off, max_ + off)
            spin.setValue(def_)

    def get_settings(self):
        msg_type = self.msgTypeCombo.currentText()
        msg_dict = {'type': msg_type}

        for label, spin, attr_name in self.__attributes(msg_type):
            if spin.isEnabled():
                offset = MidiCueSettings.OFFSETS.get(attr_name, 0)
                msg_dict[attr_name] = spin.value() - offset

        return {'message': dict_msg_to_str(msg_dict)}

    def __attributes(self, msg_type):
        for (l, s), a in zip(self._data_widgets, MIDI_MESSAGES[msg_type]):
            yield l, s, a

    def load_settings(self, settings):
        message = settings.get('message', '')
        if message:
            dict_msg = str_msg_to_dict(message)
            self.msgTypeCombo.setCurrentText(dict_msg['type'])

            for label, spin, attr_name in self.__attributes(dict_msg['type']):
                offset = MidiCueSettings.OFFSETS.get(attr_name, 0)
                spin.setValue(dict_msg.get(label.text().lower(), 0) + offset)


CueSettingsRegistry().add_item(MidiCueSettings, MidiCue)
