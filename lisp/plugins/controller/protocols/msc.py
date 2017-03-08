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
from PyQt5.QtWidgets import QGroupBox, QPushButton, QComboBox, QVBoxLayout, \
    QMessageBox, QTableView, QTableWidget, QHeaderView, QGridLayout

from lisp.modules import check_module
from lisp.modules.midi.midi_input import MIDIInput
from lisp.plugins.controller.protocols.midi import Midi
from lisp.ui.qdelegates import ComboBoxDelegate, SpinBoxDelegate, \
    CueActionDelegate, LineEditDelegate
from lisp.ui.qmodels import SimpleTableModel
from lisp.ui.settings.settings_page import CueSettingsPage
from lisp.ui.ui_utils import translate


class Msc(Midi):
    def __init__(self):
        super().__init__()

        if check_module('midi'):
            midi_input = MIDIInput()
            if not midi_input.is_open():
                midi_input.open()
            MIDIInput().new_message.connect(self.__new_message)

    def __new_message(self, message):
        if message.type == 'sysex':
            self.protocol_event.emit(Midi.str_from_message(message))

    @staticmethod
    def str_from_message(message):
        return Midi.str_from_values(message.type, message.data)

    @staticmethod
    def str_from_values(m_type, data):
        return '{} {}'.format(m_type, data)

    @staticmethod
    def from_string(message_str):
        m_type, data = message_str.split()
        return m_type, data


class MscSettings(CueSettingsPage):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'MSC Controls')

    def __init__(self, cue_class, **kwargs):
        super().__init__(cue_class, **kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.midiGroup = QGroupBox(self)
        self.midiGroup.setTitle(translate('ControllerMscSettings', 'MSC'))
        # self.midiGroup.setEnabled(check_module('midi'))
        self.midiGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.midiGroup)

        self.midiModel = SimpleTableModel([
            translate('ControllerMscSettings', 'MSC'),
            translate('ControllerMscSettings', 'Action')])

        self.midiView = MscView(cue_class, parent=self.midiGroup)
        self.midiView.setModel(self.midiModel)
        self.midiGroup.layout().addWidget(self.midiView, 0, 0, 1, 2)

        self.addButton = QPushButton(self.midiGroup)
        self.addButton.clicked.connect(self.__new_message)
        self.midiGroup.layout().addWidget(self.addButton, 1, 0)

        self.removeButton = QPushButton(self.midiGroup)
        self.removeButton.clicked.connect(self.__remove_message)
        self.midiGroup.layout().addWidget(self.removeButton, 1, 1)

        self.midiCapture = QPushButton(self.midiGroup)
        self.midiCapture.clicked.connect(self.capture_message)
        self.midiGroup.layout().addWidget(self.midiCapture, 2, 0)

        self.retranslateUi()

        self._default_action = self._cue_class.CueActions[0].name

    def retranslateUi(self):
        self.addButton.setText(translate('ControllerSettings', 'Add'))
        self.removeButton.setText(translate('ControllerSettings', 'Remove'))
        self.midiCapture.setText(translate('ControllerMscSettings', 'Capture'))

    def enable_check(self, enabled):
        self.midiGroup.setCheckable(enabled)
        self.midiGroup.setChecked(False)

    def get_settings(self):
        settings = {}
        checkable = self.midiGroup.isCheckable()

        if not (checkable and not self.midiGroup.isChecked()):
            messages = []

            for row in self.midiModel.rows:
                message = Msc.str_from_values('sysex', row[0])
                messages.append((message, row[-1]))

            if messages:
                settings['msc'] = messages

        return settings

    def load_settings(self, settings):
        if 'msc' in settings:
            for options in settings['msc']:
                m_type, data = Msc.from_string(options[0])
                self.midiModel.appendRow(data, options[1])

    def capture_message(self):
        handler = MIDIInput()
        handler.alternate_mode = True
        handler.new_message_alt.connect(self.__add_message)

        QMessageBox.information(self, '',
                                translate('ControllerMscSettings',
                                          'Listening MSC messages ...'))

        handler.new_message_alt.disconnect(self.__add_message)
        handler.alternate_mode = False

    def __add_message(self, msg):
        if self.msgTypeCombo.currentData(Qt.UserRole) == msg.type:
            self.midiModel.appendRow('',
                                     self._default_action)

    def __new_message(self):
        message_type = self.msgTypeCombo.currentData(Qt.UserRole)
        self.midiModel.appendRow('', self._default_action)

    def __remove_message(self):
        self.midiModel.removeRow(self.midiView.currentIndex().row())


class MscView(QTableView):
    def __init__(self, cue_class, **kwargs):
        super().__init__(**kwargs)

        self.delegates = [
            LineEditDelegate(),
            CueActionDelegate(cue_class=cue_class,
                              mode=CueActionDelegate.Mode.Name)
        ]

        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)

        self.setShowGrid(False)
        self.setAlternatingRowColors(True)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setHighlightSections(False)

        self.verticalHeader().sectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(24)
        self.verticalHeader().setHighlightSections(False)

        for column, delegate in enumerate(self.delegates):
            self.setItemDelegateForColumn(column, delegate)
