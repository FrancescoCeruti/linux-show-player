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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QGridLayout,
    QLabel,
    QDialogButtonBox,
    QSizePolicy,
    QPushButton,
    QTextEdit,
)

from lisp.ui.logging.common import LOG_LEVELS, LOG_ICONS_NAMES
from lisp.ui.icons import IconTheme
from lisp.ui.ui_utils import translate


class LogDialogs:
    def __init__(self, log_model, level=logging.ERROR, parent=None):
        """
        :type log_model: lisp.ui.logging.models.LogRecordModel
        """
        self._level = level
        self._log_model = log_model
        self._log_model.rowsInserted.connect(self._new_rows)

        self._mmbox = MultiMessagesBox(parent=parent)

    def _new_rows(self, parent, start, end):
        for n in range(start, end + 1):
            record = self._log_model.record(n)
            if record.levelno >= self._level:
                self._mmbox.addRecord(record)


class MultiMessagesBox(QDialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QGridLayout())
        self.setWindowModality(Qt.ApplicationModal)
        self.layout().setSizeConstraint(QGridLayout.SetFixedSize)

        self._formatter = logging.Formatter()
        self._records = []

        self.iconLabel = QLabel(self)
        self.iconLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.layout().addWidget(self.iconLabel, 0, 0)

        self.messageLabel = QLabel(self)
        self.messageLabel.setMinimumWidth(300)
        self.layout().addWidget(self.messageLabel, 0, 1)

        self.buttonBox = QDialogButtonBox(self)
        self.layout().addWidget(self.buttonBox, 1, 0, 1, 2)

        self.okButton = self.buttonBox.addButton(QDialogButtonBox.Ok)
        self.okButton.clicked.connect(self.nextRecord)

        self.dismissButton = QPushButton(self)
        self.dismissButton.setText(translate("Logging", "Dismiss all"))
        self.dismissButton.clicked.connect(self.dismissAll)
        self.dismissButton.hide()
        self.buttonBox.addButton(self.dismissButton, QDialogButtonBox.ResetRole)

        self.detailsButton = QPushButton(self)
        self.detailsButton.setCheckable(True)
        self.detailsButton.setText(translate("Logging", "Show details"))
        self.buttonBox.addButton(
            self.detailsButton, QDialogButtonBox.ActionRole
        )

        self.detailsText = QTextEdit(self)
        self.detailsText.setReadOnly(True)
        self.detailsText.setLineWrapMode(QTextEdit.NoWrap)
        self.detailsText.hide()
        self.layout().addWidget(self.detailsText, 2, 0, 1, 2)

        self.detailsButton.toggled.connect(self.detailsText.setVisible)

    def addRecord(self, record):
        self._records.append(record)
        self.updateDisplayed()

    def updateDisplayed(self):
        if self._records:
            record = self._records[-1]

            self.messageLabel.setText(record.message)
            self.iconLabel.setPixmap(
                IconTheme.get(LOG_ICONS_NAMES[record.levelname]).pixmap(32)
            )
            self.setWindowTitle(
                "{} ({})".format(
                    translate("Logging", LOG_LEVELS[record.levelname]),
                    len(self._records),
                )
            )

            # Get record details (exception traceback)
            details = ""
            if record.exc_info is not None:
                details = self._formatter.formatException(record.exc_info)

            self.detailsText.setText(details)

            width = (
                self.detailsText.document().idealWidth()
                + self.detailsText.contentsMargins().left() * 2
            )
            self.detailsText.setFixedWidth(width if width < 800 else 800)

            self.detailsButton.setVisible(bool(details))
            # If no details, than hide the widget, otherwise keep it's current
            # visibility unchanged
            if not details:
                self.detailsText.hide()

            # Show the dismiss-all button if there's more than one record
            self.dismissButton.setVisible(len(self._records) > 1)

            self.show()
            self.setMinimumSize(self.size())
            self.setMaximumSize(self.size())
        else:
            self.hide()

    def nextRecord(self):
        self._records.pop()
        self.updateDisplayed()

    def dismissAll(self):
        self._records.clear()
        self.updateDisplayed()

    def reject(self):
        self.dismissAll()
