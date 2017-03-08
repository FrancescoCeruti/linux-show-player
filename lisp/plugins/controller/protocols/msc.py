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
from PyQt5.QtWidgets import QGroupBox, QPushButton, QDialog, QVBoxLayout, \
    QTableView, QTableWidget, QHeaderView, QGridLayout, \
    QDialogButtonBox

from lisp.plugins.controller.protocols.protocol import Protocol
from lisp.modules import check_module
from lisp.modules.midi.midi_input import MIDIInput
from lisp.modules.midi.midi_msc import MscParser, MscArgument
from lisp.ui import elogging
from lisp.ui.qdelegates import CueActionDelegate, LineEditDelegate
from lisp.ui.qmodels import SimpleTableModel
from lisp.ui.settings.settings_page import CueSettingsPage
from lisp.ui.ui_utils import translate
from lisp.ui.widgets.msc_groupbox import MscGroupBox


class Msc(Protocol):
    def __init__(self):
        super().__init__()

        if check_module('midi'):
            midi_input = MIDIInput()
            if not midi_input.is_open():
                midi_input.open()
            MIDIInput().new_message.connect(self.__new_message)

    def __new_message(self, message):
        if message.type == 'sysex':
            self.protocol_event.emit(Msc.str_from_message(message))

    @staticmethod
    def str_from_message(message):
        return message.hex()

    @staticmethod
    def str_from_values(data):
        # we use hex string for now, could be sysex data (as ints)
        # msg = mido.parse([int(i, 16) for i in hex_str.split()])
        return data

    @staticmethod
    def from_string(message_str):
        # msg = mido.parse_string(message_str)
        return message_str


class MscMessageDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setLayout(QVBoxLayout())

        self.mscGroup = MscGroupBox(self)
        self.layout().addWidget(self.mscGroup)

        self.buttons = QDialogButtonBox(self)
        self.buttons.addButton(QDialogButtonBox.Cancel)
        self.buttons.addButton(QDialogButtonBox.Ok)
        self.layout().addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def get_message(self):
        return self.mscGroup.get_message()


class MscCaptureDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setLayout(QVBoxLayout())

        self.mscGroup = MscGroupBox(self)
        self.layout().addWidget(self.mscGroup)

        self.buttons = QDialogButtonBox(self)
        self.buttons.addButton(QDialogButtonBox.Cancel)
        self.buttons.addButton(QDialogButtonBox.Ok)
        self.layout().addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def get_message(self):
        return self.mscGroup.get_message()

    def add_message(self, message):
        parser = MscParser(message)

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


class MscSettings(CueSettingsPage):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'MSC Controls')

    def __init__(self, cue_class, **kwargs):
        super().__init__(cue_class, **kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.msc_dialog = MscMessageDialog(self)
        self.msc_capture_dialog = MscCaptureDialog(self)

        self.mscGroup = QGroupBox(self)
        self.mscGroup.setTitle(translate('ControllerMscSettings', 'MSC'))
        self.mscGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.mscGroup)

        self.mscModel = SimpleTableModel([
            translate('ControllerMscSettings', 'MSC'),
            translate('ControllerMscSettings', 'Action')])

        self.mscView = MscView(cue_class, parent=self.mscGroup)
        self.mscView.setModel(self.mscModel)
        self.mscGroup.layout().addWidget(self.mscView, 0, 0, 1, 2)

        self.addButton = QPushButton(self.mscGroup)
        self.addButton.clicked.connect(self.__new_message)
        self.mscGroup.layout().addWidget(self.addButton, 1, 0)

        self.removeButton = QPushButton(self.mscGroup)
        self.removeButton.clicked.connect(self.__remove_message)
        self.mscGroup.layout().addWidget(self.removeButton, 1, 1)

        self.mscCapture = QPushButton(self.mscGroup)
        self.mscCapture.clicked.connect(self.capture_message)
        self.mscGroup.layout().addWidget(self.mscCapture, 2, 0)

        self.retranslateUi()

        self._default_action = self._cue_class.CueActions[0].name

    def retranslateUi(self):
        self.addButton.setText(translate('ControllerSettings', 'Add'))
        self.removeButton.setText(translate('ControllerSettings', 'Remove'))
        self.mscCapture.setText(translate('ControllerMscSettings', 'Capture'))

    def enable_check(self, enabled):
        self.mscGroup.setCheckable(enabled)
        self.mscGroup.setChecked(False)

    def get_settings(self):
        settings = {}
        checkable = self.mscGroup.isCheckable()

        if not (checkable and not self.mscGroup.isChecked()):
            messages = []

            for row in self.mscModel.rows:
                messages.append((row[0], row[1]))

            if messages:
                settings['msc'] = messages

        return settings

    def load_settings(self, settings):
        if 'msc' in settings:
            for options in settings['msc']:
                data = Msc.from_string(options[0])
                self.mscModel.appendRow(data, options[1])

    def capture_message(self):
        handler = MIDIInput()
        handler.alternate_mode = True
        handler.new_message_alt.connect(self.__add_message)

        if self.msc_capture_dialog.exec_() == QDialog.Accepted:
            msc = self.msc_capture_dialog.get_message()
            self.mscModel.appendRow(msc.message.hex(), self._default_action)

        handler.new_message_alt.disconnect(self.__add_message)
        handler.alternate_mode = False

    def __add_message(self, msg):
        self.msc_capture_dialog.add_message(msg)

    def __new_message(self):
        if self.msc_dialog.exec_() == QDialog.Accepted:
            msc = self.msc_dialog.get_message()
            # parse back: mido.parse([int(i, 16) for i in hex_str.split()])
            self.mscModel.appendRow(msc.message.hex(), self._default_action)

    def __remove_message(self):
        self.mscModel.removeRow(self.mscView.currentIndex().row())


class MscView(QTableView):
    def __init__(self, cue_class, **kwargs):
        super().__init__(**kwargs)

        self.delegates = [
            LineEditDelegate(read_only=True),
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
