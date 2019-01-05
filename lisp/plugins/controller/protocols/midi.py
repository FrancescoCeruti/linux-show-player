# This file is part of Linux Show Player
#
# Copyright 2016 Francesco Ceruti <ceppofrancy@gmail.com>
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
from PyQt5.QtWidgets import (
    QGroupBox,
    QPushButton,
    QComboBox,
    QVBoxLayout,
    QMessageBox,
    QTableView,
    QTableWidget,
    QHeaderView,
    QGridLayout,
)

from lisp.plugins import get_plugin, PluginNotLoadedError
from lisp.plugins.controller.common import LayoutAction, tr_layout_action
from lisp.plugins.controller.protocol import Protocol
from lisp.ui.qdelegates import (
    ComboBoxDelegate,
    SpinBoxDelegate,
    CueActionDelegate,
    EnumComboBoxDelegate,
)
from lisp.ui.qmodels import SimpleTableModel
from lisp.ui.settings.pages import CuePageMixin, SettingsPage
from lisp.ui.ui_utils import translate


class MidiSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "MIDI Controls")

    def __init__(self, actionDelegate, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.midiGroup = QGroupBox(self)
        self.midiGroup.setTitle(translate("ControllerMidiSettings", "MIDI"))
        # self.midiGroup.setEnabled(check_module('midi'))
        self.midiGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.midiGroup)

        self.midiModel = SimpleTableModel(
            [
                translate("ControllerMidiSettings", "Type"),
                translate("ControllerMidiSettings", "Channel"),
                translate("ControllerMidiSettings", "Note"),
                translate("ControllerMidiSettings", "Action"),
            ]
        )

        self.midiView = MidiView(actionDelegate, parent=self.midiGroup)
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

        self.msgTypeCombo = QComboBox(self.midiGroup)
        self.msgTypeCombo.addItem(
            translate("ControllerMidiSettings", 'Filter "note on"')
        )
        self.msgTypeCombo.setItemData(0, "note_on", Qt.UserRole)
        self.msgTypeCombo.addItem(
            translate("ControllerMidiSettings", 'Filter "note off"')
        )
        self.msgTypeCombo.setItemData(1, "note_off", Qt.UserRole)
        self.midiGroup.layout().addWidget(self.msgTypeCombo, 2, 1)

        self.retranslateUi()

        self._defaultAction = None
        try:
            self.__midi = get_plugin("Midi")
        except PluginNotLoadedError:
            self.setEnabled(False)

    def retranslateUi(self):
        self.addButton.setText(translate("ControllerSettings", "Add"))
        self.removeButton.setText(translate("ControllerSettings", "Remove"))
        self.midiCapture.setText(translate("ControllerMidiSettings", "Capture"))

    def enableCheck(self, enabled):
        self.midiGroup.setCheckable(enabled)
        self.midiGroup.setChecked(False)

    def getSettings(self):
        entries = []
        for row in self.midiModel.rows:
            message = Midi.str_from_values(row[0], row[1] - 1, row[2])
            entries.append((message, row[-1]))

        return {"midi": entries}

    def loadSettings(self, settings):
        if "midi" in settings:
            for entries in settings["midi"]:
                m_type, channel, note = Midi.from_string(entries[0])
                self.midiModel.appendRow(m_type, channel + 1, note, entries[1])

    def capture_message(self):
        handler = self.__midi.input
        handler.alternate_mode = True
        handler.new_message_alt.connect(self.__add_message)

        QMessageBox.information(
            self,
            "",
            translate("ControllerMidiSettings", "Listening MIDI messages ..."),
        )

        handler.new_message_alt.disconnect(self.__add_message)
        handler.alternate_mode = False

    def __add_message(self, msg):
        if self.msgTypeCombo.currentData(Qt.UserRole) == msg.type:
            self.midiModel.appendRow(
                msg.type, msg.channel + 1, msg.note, self._defaultAction
            )

    def __new_message(self):
        message_type = self.msgTypeCombo.currentData(Qt.UserRole)
        self.midiModel.appendRow(message_type, 1, 0, self._defaultAction)

    def __remove_message(self):
        self.midiModel.removeRow(self.midiView.currentIndex().row())


class MidiCueSettings(MidiSettings, CuePageMixin):
    def __init__(self, cueType, **kwargs):
        super().__init__(
            actionDelegate=CueActionDelegate(
                cue_class=cueType, mode=CueActionDelegate.Mode.Name
            ),
            cueType=cueType,
            **kwargs,
        )
        self._defaultAction = self.cueType.CueActions[0].name


class MidiLayoutSettings(MidiSettings):
    def __init__(self, **kwargs):
        super().__init__(
            actionDelegate=EnumComboBoxDelegate(
                LayoutAction,
                mode=EnumComboBoxDelegate.Mode.Name,
                trItem=tr_layout_action,
            ),
            **kwargs,
        )
        self._defaultAction = LayoutAction.Go.name


class MidiView(QTableView):
    def __init__(self, actionDelegate, **kwargs):
        super().__init__(**kwargs)

        self.delegates = [
            ComboBoxDelegate(options=["note_on", "note_off"]),
            SpinBoxDelegate(minimum=1, maximum=16),
            SpinBoxDelegate(minimum=0, maximum=127),
            actionDelegate,
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


class Midi(Protocol):
    CueSettings = MidiCueSettings
    LayoutSettings = MidiLayoutSettings

    def __init__(self):
        super().__init__()
        # Install callback for new MIDI messages
        get_plugin("Midi").input.new_message.connect(self.__new_message)

    def __new_message(self, message):
        if message.type == "note_on" or message.type == "note_off":
            self.protocol_event.emit(Midi.str_from_message(message))

    @staticmethod
    def str_from_message(message):
        return Midi.str_from_values(message.type, message.channel, message.note)

    @staticmethod
    def str_from_values(m_type, channel, note):
        return "{} {} {}".format(m_type, channel, note)

    @staticmethod
    def from_string(message_str):
        m_type, channel, note = message_str.split()
        return m_type, int(channel), int(note)
