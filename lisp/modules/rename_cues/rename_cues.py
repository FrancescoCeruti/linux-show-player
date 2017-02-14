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

import logging
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed as futures_completed
from math import pow
from threading import Thread, Lock

import gi

from lisp.ui.ui_utils import translate

gi.require_version('Gst', '1.0')
from gi.repository import Gst
from PyQt5.QtWidgets import QMenu, QAction, QDialog, QMessageBox

from lisp.application import Application
from lisp.core.action import Action
from lisp.core.actions_handler import MainActionsHandler
from lisp.core.module import Module
from lisp.core.signal import Signal, Connection
from lisp.cues.media_cue import MediaCue
from lisp.ui.mainwindow import MainWindow
from .rename_ui import RenameUi


class RenameCues(Module):
    Name = 'RenameCues'

    def __init__(self):
        #self._gain_thread = None

        # Entry in mainWindow menu
        self.menuAction = QAction(translate('RenameCues',
                                    'Rename Cues'), MainWindow())
        self.menuAction.triggered.connect(self.rename)

        MainWindow().menuTools.addAction(self.menuAction)

    def rename(self):

        # Warning if no cue is selected
        if Application().layout.get_selected_cues() == []:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText('You have to select some cues to rename them')
            msg.exec_()
        else:
            renameUi = RenameUi(MainWindow())
            renameUi.exec_()

            if renameUi.result() == QDialog.Accepted:
                print('Actually modification of the cues')


    def terminate(self):
        MainWindow().menuTools.removeAction(self.menuAction)

