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

import traceback
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTextEdit

from lisp.ui.logging.common import LOG_ATTRIBUTES


class LogDetails(QTextEdit):
    def __init__(self, *args):
        super().__init__(*args)
        self._record = None

        self.setLineWrapMode(self.NoWrap)
        self.setReadOnly(True)

        font = QFont("Monospace")
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)

    def setLogRecord(self, record):
        self._record = record
        text = ""
        for attr, attr_text in LOG_ATTRIBUTES.items():
            text += "⇨{}:\n    {}".format(attr_text, self.formatAttribute(attr))

        self.setText(text)

    def formatAttribute(self, attribute):
        value = getattr(self._record, attribute, None)
        if attribute == "exc_info":
            if value is not None:
                return "    ".join(traceback.format_exception(*value))

        return str(value) + "\n"
