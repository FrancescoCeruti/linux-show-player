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
from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout, QFrame

from lisp.ui.icons import IconTheme


class LogStatusView(QWidget):
    double_clicked = pyqtSignal()

    def __init__(self, log_model, icons_size=16, **kwargs):
        """
        :type log_model: lisp.ui.logging.models.LogRecordModel
        """
        super().__init__(**kwargs)
        self.setLayout(QHBoxLayout())
        self.layout().setSpacing(10)
        self.layout().setContentsMargins(5, 5, 5, 5)

        self._log_model = log_model
        self._log_model.rowsInserted.connect(self._new_rows)

        self._icons_size = icons_size
        self._errors = 0
        self._warnings = 0

        self.messageLabel = QLabel(self)
        self.messageLabel.setMaximumWidth(300)
        self.layout().addWidget(self.messageLabel)

        self.line = QFrame()
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.layout().addWidget(self.line)

        self.iconWidget = QWidget(self)
        self.iconWidget.setToolTip("Errors/Warnings")
        self.iconWidget.setLayout(QHBoxLayout())
        self.iconWidget.layout().setContentsMargins(0, 0, 0, 0)
        self.iconWidget.layout().setSpacing(5)
        self.layout().addWidget(self.iconWidget)

        self.errorsCount = QLabel("0", self.iconWidget)
        self.iconWidget.layout().addWidget(self.errorsCount)

        self.errorIcon = QLabel(self.iconWidget)
        self.errorIcon.setPixmap(
            IconTheme.get("dialog-error").pixmap(icons_size)
        )
        self.iconWidget.layout().addWidget(self.errorIcon)

    def mouseDoubleClickEvent(self, e):
        self.double_clicked.emit()

    def _new_rows(self, parent, start, end):
        # Take the last record in the model
        record = self._log_model.record(self._log_model.rowCount() - 1)

        if record.levelno >= logging.INFO:
            # Display only the fist line of text
            self.messageLabel.setText(record.message.split("\n")[0])

        for n in range(start, end + 1):
            level = self._log_model.record(n).levelno
            if level >= logging.WARNING:
                self._errors += 1

        self.errorsCount.setText(str(self._errors))
