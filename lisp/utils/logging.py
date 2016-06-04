# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

"""
    Module providing a simple proxy over python-logging default module
    and optionally showing a dialog to the user.
"""

import logging
import traceback

from lisp.ui.widgets.qmessagebox import QDetailedMessageBox


def info(msg, details='', dialog=False):
    logging.info(_log_msg(msg, details))
    if dialog:
        _dialog('Information', msg, details, QDetailedMessageBox.Information)


def debug(msg, details='', dialog=False):
    logging.debug(_log_msg(msg, details))
    if dialog:
        _dialog('Debug', msg, details, QDetailedMessageBox.Information)


def warning(msg, details='', dialog=True):
    logging.warning(_log_msg(msg, details))
    if dialog:
        _dialog('Warning', msg, details, QDetailedMessageBox.Warning)


def error(msg, details='', dialog=True):
    logging.error(_log_msg(msg, details))
    if dialog:
        _dialog('Error', msg, details, QDetailedMessageBox.Critical)


def exception(msg, exception, dialog=True):
    logging.error(_log_msg(msg, traceback.format_exc()))
    if dialog:
        _dialog('Error', msg, str(exception), QDetailedMessageBox.Critical)


def _log_msg(msg, details):
    return msg + ('\nDetails: ' + details if details.strip() != '' else '')


def _dialog(title, msg, details, type_):
    QDetailedMessageBox.dgeneric(title, msg, details, type_)