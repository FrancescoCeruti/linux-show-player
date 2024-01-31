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

from abc import abstractmethod

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QComboBox,
    QSpinBox,
    QFrame,
    QWidget,
    QDialog,
    QDialogButtonBox,
)

from lisp.plugins import get_plugin
from lisp.plugins.midi.midi_utils import (
    MIDI_MSGS_SPEC,
    MIDI_ATTRS_SPEC,
    MIDI_MSGS_NAME,
    MIDI_ATTRS_NAME,
    PortDirection,
)
from lisp.ui.ui_utils import translate


class MIDIPatchCombo(QComboBox):
    def __init__(self, direction: PortDirection, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__direction = direction
        self.__midi = get_plugin("Midi")
        if self.__midi.is_loaded():
            for patch_id in self._patches():
                self.addItem("", patch_id)

    def _patches(self):
        if self.__direction is PortDirection.Input:
            return self.__midi.input_patches()
        return self.__midi.output_patches()

    def _patch_name(self, patch_id):
        if self.__direction is PortDirection.Input:
            return self.__midi.input_name_formatted(patch_id)
        return self.__midi.output_name_formatted(patch_id)

    def retranslateUi(self):
        if self.__midi.is_loaded():
            for patch_id, device_name in self._patches().items():
                self.setItemText(
                    self.findData(patch_id),
                    self._patch_name(patch_id)
                )


class MIDIMessageEdit(QWidget):
    """
    To reference naming and values see:
        https://github.com/mido/mido/blob/df6d05a6abcf6139ca31715dd3ed5450b2d98e96/mido/messages/specs.py
        https://www.midi.org/specifications-old/item/table-1-summary-of-midi-message
    """

    def __init__(self, direction: PortDirection, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.msgGroup = QGroupBox(self)
        self.msgGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.msgGroup)

        # Device patch
        self.msgPatchLabel = QLabel(self.msgGroup)
        self.msgGroup.layout().addWidget(self.msgPatchLabel, 0, 0)
        self.msgPatchCombo = MIDIPatchCombo(direction, self.msgGroup)
        self.msgGroup.layout().addWidget(self.msgPatchCombo, 0, 1)

        # Message type
        self.msgTypeLabel = QLabel(self.msgGroup)
        self.msgGroup.layout().addWidget(self.msgTypeLabel, 1, 0)
        self.msgTypeCombo = QComboBox(self.msgGroup)
        for msgType in MIDI_MSGS_SPEC.keys():
            self.msgTypeCombo.addItem(
                translate("MIDIMessageType", MIDI_MSGS_NAME[msgType]), msgType
            )
        self.msgTypeCombo.currentIndexChanged.connect(self._typeChanged)
        self.msgGroup.layout().addWidget(self.msgTypeCombo, 1, 1)

        line = QFrame(self.msgGroup)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.msgGroup.layout().addWidget(line, 2, 0, 1, 2)

        # Data widgets
        self._dataWidgets = []
        for n in range(3, 6):
            dataLabel = QLabel(self.msgGroup)
            dataSpin = QSpinBox(self.msgGroup)

            self.msgGroup.layout().addWidget(dataLabel, n, 0)
            self.msgGroup.layout().addWidget(dataSpin, n, 1)

            self._dataWidgets.append((dataSpin, dataLabel))

        self._typeChanged()
        self.retranslateUi()

    def retranslateUi(self):
        self.msgGroup.setTitle(translate("MIDICue", "MIDI Message"))
        self.msgPatchLabel.setText(translate("MIDICue", "MIDI Patch"))
        self.msgPatchCombo.retranslateUi()
        self.msgTypeLabel.setText(translate("MIDICue", "Message type"))

    def getPatchId(self):
        return self.msgPatchCombo.currentData()

    def setPatchId(self, patch_id):
        self.msgPatchCombo.setCurrentIndex(
            self.msgPatchCombo.findData(patch_id)
        )

    def getMessageDict(self):
        msgType = self.msgTypeCombo.currentData()
        msgDict = {"type": msgType}

        for attr, spin, label in self._currentValues(msgType):
            if spin.isEnabled():
                offset = MIDI_ATTRS_SPEC[attr][2]
                msgDict[attr] = spin.value() + offset

        return msgDict

    def setMessageDict(self, dictMsg):
        self.msgTypeCombo.setCurrentIndex(
            self.msgTypeCombo.findData(dictMsg["type"])
        )

        for attr, spin, label in self._currentValues(dictMsg["type"]):
            min_, _, offset = MIDI_ATTRS_SPEC.get(attr, (0, 0, 0))
            spin.setValue(dictMsg.get(attr, min_) - offset)

    def _currentValues(self, msgType):
        for attr, (spin, label) in zip(
            MIDI_MSGS_SPEC[msgType], self._dataWidgets
        ):
            yield attr, spin, label

    def _typeChanged(self):
        msgType = self.msgTypeCombo.currentData()
        for attr, spin, label in self._currentValues(msgType):
            if attr is None:
                label.setEnabled(False)
                label.setText("")

                spin.setEnabled(False)
            else:
                label.setEnabled(True)
                label.setText(MIDI_ATTRS_NAME[attr])

                min_, max_, _ = MIDI_ATTRS_SPEC[attr]
                spin.setRange(min_, max_)
                spin.setEnabled(True)


class MIDIMessageEditDialog(QDialog):
    def __init__(self, direction: PortDirection, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())

        self.editor = MIDIMessageEdit(direction)
        self.layout().addWidget(self.editor)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout().addWidget(self.buttons)

    def getMessageDict(self):
        return self.editor.getMessageDict()

    def setMessageDict(self, dictMsg):
        self.editor.setMessageDict(dictMsg)

    def getPatchId(self):
        return self.editor.getPatchId()

    def setPatchId(self, patch_id):
        return self.editor.setPatchId(patch_id)
