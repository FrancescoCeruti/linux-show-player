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

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QHeaderView, QTableView

from lisp.plugins.midi.midi_utils import (
        DEFAULT_DEVICE_NAME,
        MAX_MIDI_DEVICES,
        PortNameMatch,
)
from lisp.ui.qdelegates import (
        ComboBoxDelegate,
        LabelDelegate,
        SpinBoxDelegate,
)


class MidiIODeviceView(QTableView):

    # Deliberately not using LiSP's Signal class, as that doesn't like being
    # connected to the setEnabled method of an instance of Qt5's PushButton.
    hasSelectionChange = pyqtSignal(bool)

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
        midi_devices = list(set(midi_devices)) # Remove duplicates
        midi_devices.sort()
        self.delegates[1].options = [DEFAULT_DEVICE_NAME] + midi_devices

    def ensureOptionExists(self, entry):
        if entry not in self.delegates[1].options:
            self.delegates[1].options.insert(1, entry)

    def ensureOptionsExist(self, options):
        new_options = []
        model = self.model()
        for patch_id, device_name in options.items():
            if device_name is None or device_name in new_options or device_name in self.delegates[1].options:
                continue
            new_options.append(device_name)
        new_options.sort(reverse=True)
        for option in new_options:
            self.delegates[1].options.insert(1, option)

    def removeSelectedPatch(self):
        self.model().removePatchAtIndex(self.currentIndex())

    def selectionChanged(self, selected, deselected):
        super().selectionChanged(selected, deselected)
        self.hasSelectionChange.emit(bool(selected.indexes()))
