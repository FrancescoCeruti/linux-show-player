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

from PyQt5.QtWidgets import QHeaderView, QTableView

from lisp.plugins.midi.midi_utils import (
        DEFAULT_DEVICE_NAME,
        MAX_MIDI_DEVICES,
)
from lisp.ui.qdelegates import (
        ComboBoxDelegate,
        LabelDelegate,
        SpinBoxDelegate,
)


class MidiIODeviceView(QTableView):

    def __init__(self, model, **kwargs):
        super().__init__(**kwargs)

        self.delegates = [
            SpinBoxDelegate(minimum=1, maximum=MAX_MIDI_DEVICES),
            ComboBoxDelegate(),
            LabelDelegate(),
        ]

        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)

        self.setShowGrid(False)
        self.setAlternatingRowColors(True)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.verticalHeader().setVisible(False)
        self.verticalHeader().sectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(24)
        self.verticalHeader().setHighlightSections(False)

        self.setModel(model)

        for column, delegate in enumerate(self.delegates):
            self.setItemDelegateForColumn(column, delegate)

        self.horizontalHeader().resizeSection(0, 32)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.horizontalHeader().resizeSection(2, 64)

    def setOptions(self, midi_devices):
        self.delegates[1].options = [DEFAULT_DEVICE_NAME] + midi_devices
