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

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt

from lisp.cues.cue import Cue
from lisp.ui.ui_utils import translate

# Application defined data-roles
CueClassRole = Qt.UserRole + 1


class SimpleTableModel(QAbstractTableModel):
    """ Simple implementation of a QAbstractTableModel

    .. warning::
        Currently this is a partial implementation of a complete R/W Qt model
        intended for a simple and straightforward usage.
    """

    def __init__(self, columns):
        super().__init__()

        self.columns = columns
        self.rows = []

    def appendRow(self, *values):
        row = len(self.rows) - 1

        self.beginInsertRows(QModelIndex(), row, row)
        self.rows.append(list(values))
        self.endInsertRows()

    def removeRow(self, row, parent=QModelIndex()):
        if -1 < row < len(self.rows):
            self.beginRemoveRows(parent, row, row)
            self.rows.pop(row)
            self.endRemoveRows()
            return True
        return False

    def rowCount(self, parent=QModelIndex()):
        return len(self.rows)

    def columnCount(self, parent=QModelIndex()):
        return len(self.columns)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section < len(self.columns):
                return self.columns[section]
            else:
                return section + 1
        if role == Qt.SizeHintRole and orientation == Qt.Vertical:
            return 0

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                value = self.rows[index.row()][index.column()]
                if type(value) == bool:
                    return translate("QComboBox", str(value).title())
                else:
                    return value
            elif role == Qt.EditRole:
                return self.rows[index.row()][index.column()]
            elif role == Qt.TextAlignmentRole:
                return Qt.AlignCenter

    def setData(self, index, value, role=Qt.DisplayRole):
        if index.isValid() and (role == Qt.DisplayRole or role == Qt.EditRole):
            row = index.row()
            col = index.column()
            # Update only if value is different
            if self.rows[row][col] != value:
                self.rows[row][col] = value
                self.dataChanged.emit(
                    self.index(row, 0),
                    self.index(row, col),
                    [Qt.DisplayRole, Qt.EditRole],
                )

                return True

        return False

    def flags(self, index):
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable


class SimpleCueListModel(SimpleTableModel):
    """Extension of SimpleTableModel supporting the CueClassRole for rows."""

    def __init__(self, columns):
        super().__init__(columns)

        self.rows_cc = []

    def appendRow(self, cue_class, *values):
        self.rows_cc.append(cue_class)
        super().appendRow(*values)

    def removeRow(self, row, parent=None):
        if super().removeRow(row):
            self.rows_cc.pop(row)

    def data(self, index, role=Qt.DisplayRole):
        if role == CueClassRole and index.isValid:
            return self.rows_cc[index.row()]

        return super().data(index, role)

    def setData(self, index, value, role=Qt.DisplayRole):
        if role == CueClassRole and index.isValid():
            if issubclass(value, Cue):
                self.rows_cc[index.row()] = value
                return True

            return False

        return super().setData(index, value, role)
