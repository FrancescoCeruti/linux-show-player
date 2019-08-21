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
    QLabel,
    QHBoxLayout,
)

from lisp.plugins import get_plugin, PluginNotLoadedError
from lisp.plugins.controller.common import LayoutAction, tr_layout_action
from lisp.plugins.controller.protocol import Protocol
from lisp.plugins.midi.midi_utils import (
    MIDI_MSGS_NAME,
    midi_data_from_msg,
    midi_msg_from_data,
    midi_from_dict,
    midi_from_str,
    MIDI_MSGS_SPEC, MIDI_ATTRS_SPEC)
from lisp.plugins.midi.widgets import MIDIMessageEditDialog
from lisp.ui.qdelegates import (
    CueActionDelegate,
    EnumComboBoxDelegate,
    LabelDelegate,
)
from lisp.ui.qmodels import SimpleTableModel
from lisp.ui.settings.pages import CuePageMixin, SettingsPage
from lisp.ui.ui_utils import translate


class MidiSettings(SettingsPage):
    FILTER_ALL = "__all__"

    Name = QT_TRANSLATE_NOOP("SettingsPageName", "MIDI Controls")

    def __init__(self, actionDelegate, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.midiGroup = QGroupBox(self)
        self.midiGroup.setTitle(translate("ControllerMidiSettings", "MIDI"))
        self.midiGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.midiGroup)

        self.midiModel = MidiModel()

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

        self.filterLayout = QHBoxLayout()
        self.midiGroup.layout().addLayout(self.filterLayout, 2, 1)

        self.filterLabel = QLabel(self.midiGroup)
        self.filterLabel.setAlignment(Qt.AlignCenter)
        self.filterLayout.addWidget(self.filterLabel)

        self.filterTypeCombo = QComboBox(self.midiGroup)
        self.filterLayout.addWidget(self.filterTypeCombo)

        self.filterTypeCombo.addItem(
            translate("ControllerMidiSettings", "-- All Messages --"),
            self.FILTER_ALL,
        )
        for msg_type, msg_name in MIDI_MSGS_NAME.items():
            self.filterTypeCombo.addItem(
                translate("MIDIMessageType", msg_name), msg_type
            )

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
        self.filterLabel.setText(
            translate("ControllerMidiSettings", "Capture filter")
        )

    def enableCheck(self, enabled):
        self.midiGroup.setCheckable(enabled)
        self.midiGroup.setChecked(False)

    def getSettings(self):
        entries = []
        for row in range(self.midiModel.rowCount()):
            message, action = self.midiModel.getMessage(row)
            entries.append((str(message), action))

        return {"midi": entries}

    def loadSettings(self, settings):
        if "midi" in settings:
            for entry in settings["midi"]:
                self.midiModel.appendMessage(midi_from_str(entry[0]), entry[1])

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

    def __add_message(self, message):
        mgs_filter = self.filterTypeCombo.currentData(Qt.UserRole)
        if mgs_filter == self.FILTER_ALL or message.type == mgs_filter:
            if hasattr(message, "velocity"):
                message.velocity = 0

            self.midiModel.appendMessage(message, self._defaultAction)

    def __new_message(self):
        dialog = MIDIMessageEditDialog()
        if dialog.exec() == MIDIMessageEditDialog.Accepted:
            message = midi_from_dict(dialog.getMessageDict())
            if hasattr(message, "velocity"):
                message.velocity = 0

            self.midiModel.appendMessage(message, self._defaultAction)

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


class MidiMessageTypeDelegate(LabelDelegate):
    def _text(self, option, index):
        message_type = index.data()
        return translate(
            "MIDIMessageType", MIDI_MSGS_NAME.get(message_type, "undefined")
        )


class MidiValueDelegate(LabelDelegate):
    def _text(self, option, index):
        option.displayAlignment = Qt.AlignCenter

        value = index.data()
        if value is not None:
            model = index.model()
            message_type = model.data(model.index(index.row(), 0))
            message_spec = MIDI_MSGS_SPEC.get(message_type, ())

            if len(message_spec) >= index.column():
                attr = message_spec[index.column() - 1]
                attr_spec = MIDI_ATTRS_SPEC.get(attr)

                if MIDI_MSGS_SPEC is not None:
                    return str(value - attr_spec[-1])

        return ""


class MidiModel(SimpleTableModel):
    def __init__(self):
        super().__init__(
            [
                translate("ControllerMidiSettings", "Type"),
                translate("ControllerMidiSettings", "Data 1"),
                translate("ControllerMidiSettings", "Data 2"),
                translate("ControllerMidiSettings", "Data 3"),
                translate("ControllerMidiSettings", "Action"),
            ]
        )

    def appendMessage(self, message, action):
        data = midi_data_from_msg(message)
        data.extend((None,) * (3 - len(data)))
        self.appendRow(message.type, *data, action)

    def updateMessage(self, row, message, action):
        data = midi_data_from_msg(message)
        data.extend((None,) * (3 - len(data)))
        self.updateRow(row, message.type, *data, action)

    def getMessage(self, row):
        if row < len(self.rows):
            return (
                midi_msg_from_data(self.rows[row][0], self.rows[row][1:4]),
                self.rows[row][4],
            )

    def flags(self, index):
        if index.column() <= 3:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:
            return super().flags(index)


class MidiView(QTableView):
    def __init__(self, actionDelegate, **kwargs):
        super().__init__(**kwargs)

        self.delegates = [
            MidiMessageTypeDelegate(),
            MidiValueDelegate(),
            MidiValueDelegate(),
            MidiValueDelegate(),
            actionDelegate,
        ]

        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)

        self.setShowGrid(False)
        self.setAlternatingRowColors(True)

        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.horizontalHeader().setMinimumSectionSize(80)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setHighlightSections(False)

        self.verticalHeader().sectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(24)
        self.verticalHeader().setHighlightSections(False)

        for column, delegate in enumerate(self.delegates):
            self.setItemDelegateForColumn(column, delegate)

        self.doubleClicked.connect(self.__doubleClicked)

    def __doubleClicked(self, index):
        if index.column() <= 3:
            message, action = self.model().getMessage(index.row())

            dialog = MIDIMessageEditDialog()
            dialog.setMessageDict(message.dict())

            if dialog.exec() == MIDIMessageEditDialog.Accepted:
                self.model().updateMessage(
                    index.row(), midi_from_dict(dialog.getMessageDict()), action
                )


class Midi(Protocol):
    CueSettings = MidiCueSettings
    LayoutSettings = MidiLayoutSettings

    def __init__(self):
        super().__init__()
        # Install callback for new MIDI messages
        get_plugin("Midi").input.new_message.connect(self.__new_message)

    def __new_message(self, message):
        if hasattr(message, "velocity"):
            message.velocity = 0

        self.protocol_event.emit(str(message))
