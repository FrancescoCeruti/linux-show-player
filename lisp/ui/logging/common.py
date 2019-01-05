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

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP

LOG_LEVELS = {
    "DEBUG": QT_TRANSLATE_NOOP("Logging", "Debug"),
    "INFO": QT_TRANSLATE_NOOP("Logging", "Info"),
    "WARNING": QT_TRANSLATE_NOOP("Logging", "Warning"),
    "ERROR": QT_TRANSLATE_NOOP("Logging", "Error"),
    "CRITICAL": QT_TRANSLATE_NOOP("Logging", "Critical"),
}

LOG_ICONS_NAMES = {
    "DEBUG": "dialog-question",
    "INFO": "dialog-information",
    "WARNING": "dialog-warning",
    "ERROR": "dialog-error",
    "CRITICAL": "dialog-error",
}

LOG_ATTRIBUTES = {
    "asctime": QT_TRANSLATE_NOOP("Logging", "Time"),
    "msecs": QT_TRANSLATE_NOOP("Logging", "Milliseconds"),
    "name": QT_TRANSLATE_NOOP("Logging", "Logger name"),
    "levelname": QT_TRANSLATE_NOOP("Logging", "Level"),
    "message": QT_TRANSLATE_NOOP("Logging", "Message"),
    "funcName": QT_TRANSLATE_NOOP("Logging", "Function"),
    "pathname": QT_TRANSLATE_NOOP("Logging", "Path name"),
    "filename": QT_TRANSLATE_NOOP("Logging", "File name"),
    "lineno": QT_TRANSLATE_NOOP("Logging", "Line no."),
    "module": QT_TRANSLATE_NOOP("Logging", "Module"),
    "process": QT_TRANSLATE_NOOP("Logging", "Process ID"),
    "processName": QT_TRANSLATE_NOOP("Logging", "Process name"),
    "thread": QT_TRANSLATE_NOOP("Logging", "Thread ID"),
    "threadName": QT_TRANSLATE_NOOP("Logging", "Thread name"),
    "exc_info": QT_TRANSLATE_NOOP("Logging", "Exception info"),
}

LogRecordRole = Qt.UserRole
LogAttributeRole = Qt.UserRole + 1
