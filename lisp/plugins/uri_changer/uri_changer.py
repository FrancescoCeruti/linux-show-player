# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2015 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtWidgets import QAction

from lisp.core.plugin import Plugin
from lisp.application import Application
from .uri_changer_dialog import UriChangerDialog


class UriChanger(Plugin):

    Name = 'URI Changer'

    def __init__(self):
        self.main_window = Application().mainWindow

        self.menuAction = QAction('Session URI change', self.main_window)
        self.menuAction.triggered.connect(self.show_dialog)
        self.main_window.menuTools.addAction(self.menuAction)

    def show_dialog(self):
        dialog = UriChangerDialog(parent=self.main_window)
        dialog.exec_()

    def reset(self):
        self.main_window.menuTools.removeAction(self.menuAction)
