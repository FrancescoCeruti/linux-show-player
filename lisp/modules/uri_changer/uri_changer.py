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

from PyQt5.QtWidgets import QAction

from lisp.core.module import Module
from lisp.ui.mainwindow import MainWindow
from lisp.ui.ui_utils import translate
from .uri_changer_dialog import UriChangerDialog


class UriChanger(Module):
    Name = 'URI Changer'

    def __init__(self):
        self.menuAction = QAction(translate('UriChanger', 'Session URI change'),
                                  MainWindow())
        self.menuAction.triggered.connect(self.show_dialog)

        MainWindow().menuTools.addAction(self.menuAction)

    def show_dialog(self):
        dialog = UriChangerDialog(parent=MainWindow())
        dialog.exec_()

    def terminate(self):
        MainWindow().menuTools.removeAction(self.menuAction)
