# This file is part of Linux Show Player
#
# Copyright 2023 Francesco Ceruti <ceppofrancy@gmail.com>
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

from lisp.plugins import get_plugin
from lisp.core.plugin import PluginNotLoadedError
from lisp.plugins.controller.common import LayoutAction, tr_layout_action
from lisp.plugins.controller.protocol import Protocol
from lisp.ui.qdelegates import (
    CueActionDelegate,
    EnumComboBoxDelegate,
    LabelDelegate,
)
from lisp.ui.qmodels import SimpleTableModel
from lisp.ui.settings.pages import CuePageMixin, SettingsPage
from lisp.ui.ui_utils import translate

try:
    from lisp.plugins.midi.midi_utils import (
        MIDI_MSGS_NAME,
        midi_data_from_msg,
        midi_msg_from_data,
        midi_from_dict,
        midi_from_str,
        MIDI_MSGS_SPEC,
        MIDI_ATTRS_SPEC,
        PortDirection,
    )
    from lisp.plugins.midi.widgets import MIDIPatchCombo, MIDIMessageEditDialog
except ImportError:
    midi_from_str = lambda *_: None


logger = logging.getLogger(__name__)


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

        try:
            self.__midi = get_plugin("Midi")
        except PluginNotLoadedError:
            self.setEnabled(False)
            self.midiNotInstalledMessage = QLabel()
            self.midiNotInstalledMessage.setAlignment(Qt.AlignCenter)
            self.midiGroup.layout().addWidget(self.midiNotInstalledMessage)
            self.retranslateUi()
            return

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

        self.filterPatchCombo = MIDIPatchCombo(PortDirection.Input, self.midiGroup)
        self.filterLayout.addWidget(self.filterPatchCombo)

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

    def retranslateUi(self):
        if hasattr(self, "midiNotInstalledMessage"):
            self.midiNotInstalledMessage.setText(
                translate("ControllerSettings", "MIDI plugin not installed"))
            return

        self.addButton.setText(translate("ControllerSettings", "Add"))
        self.removeButton.setText(translate("ControllerSettings", "Remove"))

        self.midiCapture.setText(translate("ControllerMidiSettings", "Capture"))
        self.filterLabel.setText(
            translate("ControllerMidiSettings", "Capture filter")
        )
        self.filterPatchCombo.retranslateUi()

    def enableCheck(self, enabled):
        self.setGroupEnabled(self.midiGroup, enabled)

    def getSettings(self):
        entries = []
        for row in range(self.midiModel.rowCount()):
            patch_id = self.midiModel.getPatchId(row)
            message, action = self.midiModel.getMessage(row)
            entries.append((f"{patch_id} {str(message)}", action))

        return {"midi": entries}

    def loadSettings(self, settings):
        for entry in settings.get("midi", ()):
            try:
                entry_split = entry[0].split(" ", 1)
                if '#' not in entry_split[0]:
                    # Backwards compatibility for config without patches
                    self.midiModel.appendMessage("in#1", midi_from_str(entry[0]), entry[1])
                else:
                    self.midiModel.appendMessage(entry_split[0], midi_from_str(entry_split[1]), entry[1])
            except Exception:
                logger.warning(
                    translate(
                        "ControllerMidiSettingsWarning",
                        "Error while importing configuration entry, skipped.",
                    ),
                    exc_info=True,
                )

    def capture_message(self):
        settings = [
            self.filterPatchCombo.currentData(),
            self.__add_message
        ]
        if self.__midi.add_exclusive_callback(*settings):
            QMessageBox.information(
                self,
                "",
                translate("ControllerMidiSettings", "Listening MIDI messages ..."),
            )
            self.__midi.remove_exclusive_callback(*settings)

    def __add_message(self, patch_id, message):
        mgs_filter = self.filterTypeCombo.currentData(Qt.UserRole)
        if mgs_filter == self.FILTER_ALL or message.type == mgs_filter:
            if hasattr(message, "velocity"):
                message = message.copy(velocity=0)

            self.midiModel.appendMessage(patch_id, message, self._defaultAction)

    def __new_message(self):
        dialog = MIDIMessageEditDialog(PortDirection.Input)
        if dialog.exec() == MIDIMessageEditDialog.Accepted:
            message = midi_from_dict(dialog.getMessageDict())
            patch_id = dialog.getPatchId()
            if hasattr(message, "velocity"):
                message.velocity = 0

            self.midiModel.appendMessage(patch_id, message, self._defaultAction)

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
            message_type = model.data(model.index(index.row(), 1))
            message_spec = MIDI_MSGS_SPEC.get(message_type, ())

            if len(message_spec) >= index.column() - 1:
                attr = message_spec[index.column() - 2]
                attr_spec = MIDI_ATTRS_SPEC.get(attr)

                if attr_spec is not None:
                    return str(value - attr_spec[-1])

        return ""


class MidiModel(SimpleTableModel):
    def __init__(self):
        super().__init__(
            [
                translate("ControllerMidiSettings", "MIDI Patch"),
                translate("ControllerMidiSettings", "Type"),
                translate("ControllerMidiSettings", "Data 1"),
                translate("ControllerMidiSettings", "Data 2"),
                translate("ControllerMidiSettings", "Data 3"),
                translate("ControllerMidiSettings", "Action"),
            ]
        )
        try:
            self.__midi = get_plugin("Midi")
            if not self.__midi.is_loaded():
                self.__midi = None
        except PluginNotLoadedError:
            self.__midi = None

    def appendMessage(self, patch_id, message, action):
        if not self.__midi:
            return
        data = midi_data_from_msg(message)
        data.extend((None,) * (3 - len(data)))
        self.appendRow(patch_id, message.type, *data, action)

    def updateMessage(self, row, patch_id, message, action):
        data = midi_data_from_msg(message)
        data.extend((None,) * (3 - len(data)))
        self.updateRow(row, patch_id, message.type, *data, action)

    def getMessage(self, row):
        if row < len(self.rows):
            return (
                midi_msg_from_data(self.rows[row][1], self.rows[row][2:5]),
                self.rows[row][5],
            )

    def getPatchId(self, row):
        if row < len(self.rows):
            return self.rows[row][0]

    def flags(self, index):
        if index.column() <= 4:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:
            return super().flags(index)

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and index.column() == 0 and role == Qt.DisplayRole:
            return f"{self.__midi.input_name_formatted(self.getPatchId(index.row()))[:16]}..."

        return super().data(index, role)


class MidiView(QTableView):
    def __init__(self, actionDelegate, **kwargs):
        super().__init__(**kwargs)

        self.delegates = [
            LabelDelegate(),
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
        if index.column() <= 4:
            patch_id = self.model().getPatchId(index.row())
            message, action = self.model().getMessage(index.row())

            dialog = MIDIMessageEditDialog(PortDirection.Input)
            dialog.setPatchId(patch_id)
            dialog.setMessageDict(message.dict())

            if dialog.exec() == MIDIMessageEditDialog.Accepted:
                self.model().updateMessage(
                    index.row(), dialog.getPatchId(), midi_from_dict(dialog.getMessageDict()), action
                )


class Midi(Protocol):
    CueSettings = MidiCueSettings
    LayoutSettings = MidiLayoutSettings

    def __init__(self):
        super().__init__()
        try:
            # Install callback for new MIDI messages
            midi = get_plugin("Midi")
            if midi.is_loaded():
                midi.received.connect(self.__new_message)
        except PluginNotLoadedError:
            pass

    def __new_message(self, patch_id, message):
        if hasattr(message, "velocity"):
            message = message.copy(velocity=0)

        self.protocol_event.emit(f"{patch_id} {str(message)}")
