# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2018 Francesco Ceruti <ceppofrancy@gmail.com>
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
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QComboBox,
    QSpinBox,
    QFrame,
    QWidget,
)

from lisp.ui.ui_utils import translate


class MIDIMessageEdit(QWidget):
    """
    To reference naming and values see:
        https://github.com/mido/mido/blob/df6d05a6abcf6139ca31715dd3ed5450b2d98e96/mido/messages/specs.py
        https://www.midi.org/specifications-old/item/table-1-summary-of-midi-message
    """

    MESSAGES = {
        "note_on": ["channel", "note", "velocity"],
        "note_off": ["channel", "note", "velocity"],
        "polytouch": ["channel", "note", "value"],
        "control_change": ["channel", "control", "value"],
        "program_change": ["channel", "program", None],
        "aftertouch": ["channel", "value", None],
        "pitchwheel": ["channel", "pitch", None],
        "song_select": ["song", None, None],
        "songpos": ["pos", None, None],
        "start": [None] * 3,
        "stop": [None] * 3,
        "continue": [None] * 3,
    }

    ATTRIBUTES = {
        "channel": (1, 16, -1),
        "note": (0, 127, 0),
        "velocity": (0, 127, 0),
        "control": (0, 127, 0),
        "program": (0, 127, 0),
        "value": (0, 127, 0),
        "song": (0, 127, 0),
        "pitch": (-8192, 8191, 0),
        "pos": (0, 16383, 0),
    }

    MESSAGES_UI = {
        "note_on": QT_TRANSLATE_NOOP("MIDIMessageType", "Note ON"),
        "note_off": QT_TRANSLATE_NOOP("MIDIMessageType", "Note OFF"),
        "polytouch": QT_TRANSLATE_NOOP(
            "MIDIMessageType", "Polyphonic After-touch"
        ),
        "control_change": QT_TRANSLATE_NOOP(
            "MIDIMessageType", "Control/Mode Change"
        ),
        "program_change": QT_TRANSLATE_NOOP(
            "MIDIMessageType", "Program Change"
        ),
        "aftertouch": QT_TRANSLATE_NOOP(
            "MIDIMessageType", "Channel After-touch"
        ),
        "pitchwheel": QT_TRANSLATE_NOOP("MIDIMessageType", "Pitch Bend Change"),
        "song_select": QT_TRANSLATE_NOOP("MIDIMessageType", "Song Select"),
        "songpos": QT_TRANSLATE_NOOP("MIDIMessageType", "Song Position"),
        "start": QT_TRANSLATE_NOOP("MIDIMessageType", "Start"),
        "stop": QT_TRANSLATE_NOOP("MIDIMessageType", "Stop"),
        "continue": QT_TRANSLATE_NOOP("MIDIMessageType", "Continue"),
    }

    ATTRIBUTES_UI = {
        "channel": QT_TRANSLATE_NOOP("MIDIMessageAttr", "Channel"),
        "note": QT_TRANSLATE_NOOP("MIDIMessageAttr", "Note"),
        "velocity": QT_TRANSLATE_NOOP("MIDIMessageAttr", "Velocity"),
        "control": QT_TRANSLATE_NOOP("MIDIMessageAttr", "Control"),
        "program": QT_TRANSLATE_NOOP("MIDIMessageAttr", "Program"),
        "value": QT_TRANSLATE_NOOP("MIDIMessageAttr", "Value"),
        "song": QT_TRANSLATE_NOOP("MIDIMessageAttr", "Song"),
        "pitch": QT_TRANSLATE_NOOP("MIDIMessageAttr", "Pitch"),
        "pos": QT_TRANSLATE_NOOP("MIDIMessageAttr", "Position"),
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
        for msgType in MIDIMessageEdit.MESSAGES.keys():
            self.msgTypeCombo.addItem(
                translate(
                    "MIDIMessageType", MIDIMessageEdit.MESSAGES_UI[msgType]
                ),
                msgType,
            )
        self.msgTypeCombo.currentIndexChanged.connect(self._typeChanged)
        self.msgGroup.layout().addWidget(self.msgTypeCombo, 0, 1)

        line = QFrame(self.msgGroup)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.msgGroup.layout().addWidget(line, 1, 0, 1, 2)

        # Data widgets
        self._dataWidgets = []
        for n in range(2, 5):
            dataLabel = QLabel(self.msgGroup)
            dataSpin = QSpinBox(self.msgGroup)

            self.msgGroup.layout().addWidget(dataLabel, n, 0)
            self.msgGroup.layout().addWidget(dataSpin, n, 1)

            self._dataWidgets.append((dataSpin, dataLabel))

        self._typeChanged()
        self.retranslateUi()

    def retranslateUi(self):
        self.msgGroup.setTitle(translate("MIDICue", "MIDI Message"))
        self.msgTypeLabel.setText(translate("MIDICue", "Message type"))

    def getMessageDict(self):
        msgType = self.msgTypeCombo.currentData()
        msgDict = {"type": msgType}

        for attr, spin, label in self._currentValues(msgType):
            if spin.isEnabled():
                offset = MIDIMessageEdit.ATTRIBUTES[attr][2]
                msgDict[attr] = spin.value() + offset

        return msgDict

    def setMessageDict(self, dictMsg):
        self.msgTypeCombo.setCurrentIndex(
            self.msgTypeCombo.findData(dictMsg["type"])
        )

        for attr, spin, label in self._currentValues(dictMsg["type"]):
            min_, _, offset = MIDIMessageEdit.ATTRIBUTES.get(attr, (0, 0, 0))
            spin.setValue(dictMsg.get(attr, min_) - offset)

    def _currentValues(self, msgType):
        for attr, (spin, label) in zip(
            MIDIMessageEdit.MESSAGES[msgType], self._dataWidgets
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
                label.setText(MIDIMessageEdit.ATTRIBUTES_UI[attr])

                min_, max_, _ = MIDIMessageEdit.ATTRIBUTES[attr]
                spin.setRange(min_, max_)
                spin.setEnabled(True)
