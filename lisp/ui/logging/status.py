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

import logging

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout, QSizePolicy

from lisp.ui.icons import IconTheme
from lisp.ui.ui_utils import translate


class LogStatusIcon(QWidget):
    double_clicked = pyqtSignal()

    def __init__(self, log_model, icons_size=16, **kwargs):
        """
        :type log_model: lisp.ui.logging.models.LogRecordModel
        """
        super().__init__(**kwargs)
        self.setLayout(QHBoxLayout())
        self.setToolTip(translate("LogStatusIcon", "Errors/Warnings"))
        self.layout().setSpacing(5)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._log_model = log_model
        self._log_model.rowsInserted.connect(self._newRows)

        self._icons_size = icons_size
        self._errors = 0

        self.errorsCount = QLabel("0", self)
        self.errorsCount.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.layout().addWidget(self.errorsCount)

        self.errorIcon = QLabel(self)
        self.errorIcon.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.errorIcon.setPixmap(
            IconTheme.get("dialog-error").pixmap(icons_size)
        )
        self.layout().addWidget(self.errorIcon)

    def mouseDoubleClickEvent(self, e):
        self.double_clicked.emit()

    def _newRows(self, parent, start, end):
        for n in range(start, end + 1):
            level = self._log_model.record(n).levelno
            if level >= logging.WARNING:
                self._errors += 1

        self.errorsCount.setText(str(self._errors))


class LogMessageWidget(QLabel):
    def __init__(self, log_model, parent=None):
        """
        :type log_model: lisp.ui.logging.models.LogRecordModel
        """
        super().__init__(parent)
        self._log_model = log_model
        self._log_model.rowsInserted.connect(self._newRows)

    def _newRows(self, parent, start, end):
        # Take the last record in the model
        record = self._log_model.record(end)

        if record.levelno >= logging.INFO:
            # Display only the fist line of text
            self.setText(record.message.split("\n")[0])
