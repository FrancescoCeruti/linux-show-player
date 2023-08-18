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
import logging

from PyQt5.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    Qt,
    QT_TRANSLATE_NOOP,
)

from lisp.plugins import get_plugin
from lisp.plugins.midi.midi_io import MIDIInput, MIDIOutput
from lisp.plugins.midi.midi_utils import (
    DEFAULT_DEVICE_NAME,
    MAX_MIDI_DEVICES,
    midi_input_names,
    midi_output_names,
    PortStatus,
)
from lisp.ui.ui_utils import translate


logger = logging.getLogger(__name__)


class MidiIODeviceModel(QAbstractTableModel):

    def __init__(self):
        super().__init__()

        self.patches = []
        self.columns = [
            translate("MIDISettings", "#"),
            translate("MIDISettings", "Device"),
            translate("MIDISettings", "Status"),
        ]
        self.used_numids = []

    def appendPatch(self, port_name=DEFAULT_DEVICE_NAME, numid=0):
        if len(self.used_numids) == MAX_MIDI_DEVICES:
            logger.warning("Arbitrary maximum number of MIDI devices reached.")
            return

        if numid == 0:
            for candidate in range(1, MAX_MIDI_DEVICES + 1):
                if candidate not in self.used_numids:
                    numid = candidate
                    break
        elif numid in self.used_numids:
            logger.warning("Provided ID already used. Refusing to add.")
            return

        self.used_numids.append(numid)
        self.used_numids.sort()

        row = self.used_numids.index(numid)
        self.beginInsertRows(QModelIndex(), row, row)
        patch = {
            "id": numid,
            "device": port_name,
            "status": self.portStatus(numid, port_name),
        }
        self.patches.insert(row, patch)
        self.endInsertRows()

    def columnCount(self, parent=QModelIndex()):
        return len(self.columns)

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            column = index.column()
            patch = self.patches[index.row()]

            if role == Qt.TextAlignmentRole:
                if column == 1:
                    return Qt.AlignLeft | Qt.AlignVCenter
                else:
                    return Qt.AlignCenter

            if role == Qt.DisplayRole:
                if column == 0:
                    return patch["id"]
                elif column == 1:
                    return patch["device"]
                elif column == 2:
                    return patch["status"].value

            if role == Qt.EditRole and column == 1:
                return patch["device"]

    def deserialise(self, settings):
        if isinstance(settings, str):
            self.appendPatch(settings)

    def flags(self, index):
        column = index.column()
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if column == 1:
            flags |= Qt.ItemIsEditable

        return flags

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section < len(self.columns):
                return self.columns[section]
            else:
                return section + 1

    @abstractmethod
    def portStatus(self, numid, port_name):
        pass

    def rowCount(self, parent=QModelIndex()):
        return len(self.patches)

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or role != Qt.EditRole:
            return False
        
        column = index.column()
        if column != 1:
            return False

        row = index.row()
        patch = self.patches[row]
        patch["device"] = value

        status_updated = self._updateStatus(row)
        self.dataChanged.emit(
            self.index(row, 1), # from top-left
            self.index(row, 2 if status_updated else 1), # to bottom-right
            [Qt.DisplayRole, Qt.EditRole],
        )
        return True

    def _updateStatus(self, row):
        patch = self.patches[row]
        status = self.portStatus(patch["id"], patch["device"])
        if status != patch["status"]:
            patch["status"] = status
            return True
        return False

    def updateStatuses(self):
        for row in range(len(self.patches)):
            if self._updateStatus(row):
                self.dataChanged.emit(
                    self.index(row, 2), # from top-left
                    self.index(row, 2), # to bottom-right
                    [Qt.DisplayRole],
                )

class MidiInputDeviceModel(MidiIODeviceModel):

    def portStatus(self, numid, port_name):
        patch_id = f"in#{numid}"
        plugin = get_plugin("Midi")
        status = plugin.input_status(patch_id)
        if status is PortStatus.DoesNotExist or plugin.input_name(patch_id) != port_name:
            return PortStatus.DoesNotExist
        return status

class MidiOutputDeviceModel(MidiIODeviceModel):

    def portStatus(self, numid, port_name):
        patch_id = f"out#{numid}"
        plugin = get_plugin("Midi")
        status = plugin.output_status(patch_id)
        print(status)
        if status is PortStatus.DoesNotExist or plugin.output_name(patch_id) != port_name:
            return PortStatus.DoesNotExist
        return status
