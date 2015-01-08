##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

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
