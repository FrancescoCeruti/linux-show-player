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

import gi
from PyQt5.QtWidgets import QAction, QDialog, QMessageBox

from lisp.application import Application
from lisp.core.module import Module
from lisp.ui.mainwindow import MainWindow
from lisp.ui.ui_utils import translate
from .rename_ui import RenameUi

gi.require_version('Gst', '1.0')


class RenameCues(Module):
    Name = 'RenameCues'

    def __init__(self):
        # Entry in mainWindow menu
        self.menuAction = QAction(translate('RenameCues',
                                    'Rename Cues'), MainWindow())
        self.menuAction.triggered.connect(self.rename)

        MainWindow().menuTools.addAction(self.menuAction)

    def rename(self):
        # Initiate rename windows
        renameUi = RenameUi(MainWindow())
        # Different behaviour if no cues are selected
        if Application().layout.get_selected_cues() == []:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(translate('RenameCues',
                "No cues are selected. Rename tool will display all your cues.\n"))
            msg.exec_()

            renameUi.get_all_cues()
        else:
            renameUi.get_selected_cues()

        renameUi.exec_()

        if renameUi.result() == QDialog.Accepted:
            renameUi.record_cues_name()

    def terminate(self):
        MainWindow().menuTools.removeAction(self.menuAction)
