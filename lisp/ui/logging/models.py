# This file is part of Linux Show Player
#
# Copyright 2018 Francesco Ceruti <ceppofrancy@gmail.com>
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

from collections import deque

from PyQt5.QtCore import (
    QModelIndex,
    Qt,
    QSortFilterProxyModel,
    QAbstractTableModel,
)
from PyQt5.QtGui import QFont, QColor

from lisp.core.util import typename
from lisp.ui.logging.common import (
    LogRecordRole,
    LOG_ATTRIBUTES,
    LogAttributeRole,
)


class LogRecordModel(QAbstractTableModel):
    Font = QFont("Monospace")
    Font.setStyleHint(QFont.Monospace)

    def __init__(self, columns, bg, fg, limit=0, **kwargs):
        """
        :param columns: column to be display
        :type columns: dict[str, str]
        :type bg: dict[str, QColor]
        :type fg: dict[str, QColor]
        :param limit: maximum number of stored records, 0 means no limit
        :type limit: int
        """
        super().__init__(**kwargs)

        self._columns = list(columns.keys())
        self._columns_names = [columns[key] for key in self._columns]
        self._records = deque()
        self._limit = limit

        self._backgrounds = bg
        self._foregrounds = fg

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0

        return len(self._columns)

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0

        return len(self._records)

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            record = self._records[index.row()]

            if role == Qt.DisplayRole:
                try:
                    return getattr(record, self._columns[index.column()])
                except AttributeError:
                    pass
            elif role == Qt.BackgroundColorRole:
                return self._backgrounds.get(record.levelname)
            elif role == Qt.ForegroundRole:
                return self._foregrounds.get(record.levelname)
            elif role == Qt.FontRole:
                return LogRecordModel.Font
            elif role == LogRecordRole:
                return record

    def headerData(self, index, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and index < len(self._columns_names):
            if role == LogAttributeRole:
                return self._columns[index]
            elif role == Qt.DisplayRole:
                return self._columns_names[index]

    def append(self, record):
        pos = len(self._records)

        if self._limit and pos >= self._limit:
            self.beginRemoveRows(QModelIndex(), 0, 0)
            self._records.popleft()
            self.endRemoveRows()
            pos -= 1

        self.beginInsertRows(QModelIndex(), pos, pos)
        self._records.append(record)
        self.endInsertRows()

    def clear(self):
        self._records.clear()
        self.reset()

    def record(self, pos):
        return self._records[pos]


class LogRecordFilterModel(QSortFilterProxyModel):
    def __init__(self, levels, **kwargs):
        super().__init__(**kwargs)
        self._levels = set(levels)

    def showLevel(self, name):
        self._levels.add(name)
        self.invalidateFilter()

    def hideLevel(self, name):
        self._levels.discard(name)
        self.invalidateFilter()

    def setSourceModel(self, source_model):
        """
        :type source_model: LogRecordModel
        """
        if isinstance(source_model, LogRecordModel):
            super().setSourceModel(source_model)
        else:
            raise TypeError(
                "LogRecordFilterModel source must be LogRecordModel, not {}".format(
                    typename(source_model)
                )
            )

    def filterAcceptsRow(self, source_row, source_parent):
        if self.sourceModel() is not None:
            record = self.sourceModel().record(source_row)
            return record.levelname in self._levels

        return False


def log_model_factory(config):
    # Get logging configuration
    limit = config.get("logging.limit", 0)
    levels_background = {
        level: QColor(*color)
        for level, color in config.get("logging.backgrounds", {}).items()
    }
    levels_foreground = {
        level: QColor(*color)
        for level, color in config.get("logging.foregrounds", {}).items()
    }

    # Return a new model to store logging records
    return LogRecordModel(
        LOG_ATTRIBUTES, levels_background, levels_foreground, limit=limit
    )
