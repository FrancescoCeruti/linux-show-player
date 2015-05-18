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

import os
import traceback

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QStatusBar, \
    QMenuBar, QMenu, QAction, qApp, QSizePolicy, QFileDialog, QDialog, \
    QMessageBox

from lisp.ui import about
from lisp.utils import configuration
from lisp.utils import logging
from lisp.core.actions_handler import ActionsHandler
from lisp.core.singleton import QSingleton
from lisp.cues.cue_factory import CueFactory
from lisp.ui.settings.app_settings import AppSettings


class MainWindow(QMainWindow, metaclass=QSingleton):
    new_session = QtCore.pyqtSignal()
    save_session = QtCore.pyqtSignal(str)
    open_session = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 300)

        self._cue_add_menu = {}
        self.layout = None

        # Define the layout and the main gui's elements
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(2, 5, 2, 0)

        # Status Bar
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)
        ActionsHandler().action_done.connect(self._action_done)
        ActionsHandler().action_undone.connect(self._action_undone)
        ActionsHandler().action_redone.connect(self._action_redone)

        # Menubar
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 0, 25))
        self.menubar.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)

        self.menuFile = QMenu(self.menubar)
        self.menuEdit = QMenu(self.menubar)
        self.menuLayout = QMenu(self.menubar)
        self.menuTools = QMenu(self.menubar)
        self.menuAbout = QMenu(self.menubar)

        self.menubar.addMenu(self.menuFile)
        self.menubar.addMenu(self.menuEdit)
        self.menubar.addMenu(self.menuLayout)
        self.menubar.addMenu(self.menuTools)
        self.menubar.addMenu(self.menuAbout)

        self.setMenuBar(self.menubar)

        # menuFile
        self.newSessionAction = QAction(self, triggered=self._startup)
        self.openSessionAction = QAction(self, triggered=self._load_from_file)
        self.saveSessionAction = QAction(self, triggered=self.save)
        self.saveSessionWithName = QAction(self, triggered=self.save_with_name)
        self.editPreferences = QAction(self, triggered=self.show_preferences)
        self.fullScreenAction = QAction(self, triggered=self._fullscreen)
        self.fullScreenAction.setCheckable(True)
        self.exitAction = QAction(self, triggered=self.exit)

        self.menuFile.addAction(self.newSessionAction)
        self.menuFile.addAction(self.openSessionAction)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.saveSessionAction)
        self.menuFile.addAction(self.saveSessionWithName)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.editPreferences)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.fullScreenAction)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.exitAction)

        # menuEdit
        self.actionUndo = QAction(self)
        self.actionUndo.triggered.connect(
            lambda: ActionsHandler().undo_action())
        self.actionRedo = QAction(self)
        self.actionRedo.triggered.connect(
            lambda: ActionsHandler().redo_action())
        self.multiEdit = QAction(self)
        self.selectAll = QAction(self)
        self.deselectAll = QAction(self)
        self.invertSelection = QAction(self)

        self.cueSeparator = self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addAction(self.actionRedo)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.selectAll)
        self.menuEdit.addAction(self.deselectAll)
        self.menuEdit.addAction(self.invertSelection)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.multiEdit)

        # menuAbout
        self.actionAbout = QAction(self)
        self.actionAbout.triggered.connect(about.About(self).show)

        self.actionAbout_Qt = QAction(self)
        self.actionAbout_Qt.triggered.connect(qApp.aboutQt)

        self.menuAbout.addAction(self.actionAbout)
        self.menuAbout.addSeparator()
        self.menuAbout.addAction(self.actionAbout_Qt)

        # Set component text
        self.retranslateUi()
        # The save file name
        self.file = ''

    def retranslateUi(self):
        self.setWindowTitle('Linux Show Player')
        # menuFile
        self.menuFile.setTitle("&File")
        self.newSessionAction.setText("New session")
        self.newSessionAction.setShortcut("CTRL+N")
        self.openSessionAction.setText("Open")
        self.openSessionAction.setShortcut("CTRL+O")
        self.saveSessionAction.setText("Save session")
        self.saveSessionAction.setShortcut("CTRL+S")
        self.editPreferences.setText("Preferences")
        self.editPreferences.setShortcut("CTRL+P")
        self.saveSessionWithName.setText("Save with name")
        self.saveSessionWithName.setShortcut('CTRL+SHIFT+S')
        self.fullScreenAction.setText('Toggle fullscreen')
        self.fullScreenAction.setShortcut('F11')
        self.exitAction.setText("Exit")
        # menuEdit
        self.menuEdit.setTitle("&Edit")
        self.actionUndo.setText('Undo')
        self.actionUndo.setShortcut('CTRL+Z')
        self.actionRedo.setText('Redo')
        self.actionRedo.setShortcut('CTRL+Y')
        self.selectAll.setText("Select all")
        self.selectAll.setShortcut("CTRL+A")
        self.deselectAll.setText("Deselect all")
        self.deselectAll.setShortcut("CTRL+SHIFT+A")
        self.invertSelection.setText("Invert selection")
        self.invertSelection.setShortcut("CTRL+I")
        self.multiEdit.setText("Edit selected media")
        self.multiEdit.setShortcut("CTRL+SHIFT+E")
        # menuLayout
        self.menuLayout.setTitle("&Layout")
        # menuTools
        self.menuTools.setTitle("&Tools")
        self.multiEdit.setText("Edit selected media")
        # menuAbout
        self.menuAbout.setTitle("&About")
        self.actionAbout.setText("About")
        self.actionAbout_Qt.setText("About Qt")

    def set_layout(self, layout):
        if self.layout is not None:
            self.layout.hide()
            self.gridLayout.removeWidget(self.layout)

            self.multiEdit.triggered.disconnect()
            self.selectAll.triggered.disconnect()
            self.deselectAll.triggered.disconnect()
            self.invertSelection.triggered.disconnect()

        self.layout = layout

        self.multiEdit.triggered.connect(self.layout.edit_selected_cues)
        self.selectAll.triggered.connect(self.layout.select_all)
        self.deselectAll.triggered.connect(self.layout.deselect_all)
        self.invertSelection.triggered.connect(self.layout.invert_selection)

        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.layout.setSizePolicy(sizePolicy)
        self.gridLayout.addWidget(self.layout, 0, 0)

        self.layout.show()

    def save(self):
        if self.file == '':
            self.save_with_name()
        else:
            self.save_session.emit(self.file)

    def save_with_name(self):
        self.file, _ = QFileDialog.getSaveFileName(parent=self,
                                                   filter='*.lsp',
                                                   directory=os.getenv('HOME'))
        if self.file != '':
            if not self.file.endswith('.lsp'):
                self.file += '.lsp'
            self.save()

    def show_preferences(self):
        prefUi = AppSettings(configuration.config_to_dict(), parent=self)
        prefUi.exec_()

        if (prefUi.result() == QDialog.Accepted):
            configuration.update_config_from_dict(prefUi.get_configuraton())

    def exit(self):
        confirm = QMessageBox.Yes
        if not ActionsHandler().is_saved():
            confirm = QMessageBox.question(self, 'Exit',
                                           'The current session is not saved. '
                                           'Exit anyway?')

        if confirm == QMessageBox.Yes:
            qApp.quit()

    def closeEvent(self, event):
        self.exit()
        event.ignore()

    def register_cue_builder(self, builder):
        # TODO: implementation
        pass

    def register_cue_menu_action(self, name, function, category='', shortcut=''):
        """Register a new-cue choice for the edit-menu

        param name: The name for the MenuAction
        param function: The function that add the new cue(s)
        param category: The optional menu where insert the MenuAction
        param shortcut: An optional shortcut for the MenuAction
        """
        action = QAction(self)
        action.setText(name)
        action.triggered.connect(function)
        if shortcut != '':
            action.setShortcut(shortcut)

        if category != '':
            if category not in self._cue_add_menu:
                menu = QMenu(category, self)
                self._cue_add_menu[category] = menu
                self.menuEdit.insertMenu(self.cueSeparator, menu)

            self._cue_add_menu[category].addAction(action)
        else:
            self.menuEdit.insertAction(self.cueSeparator, action)

    def update_window_title(self):
        saved = ActionsHandler().is_saved()
        if not saved and not self.windowTitle()[0] == '*':
            self.setWindowTitle('*' + self.windowTitle())
        elif saved and self.windowTitle()[0] == '*':
            self.setWindowTitle(self.windowTitle()[1:])

    def _action_done(self, action):
        self.statusBar.showMessage(action.log())
        self.update_window_title()

    def _action_undone(self, action):
        self.statusBar.showMessage('Undone' + action.log())
        self.update_window_title()

    def _action_redone(self, action):
        self.statusBar.showMessage('Redone' + action.log())
        self.update_window_title()

    def _load_from_file(self):
        if self._new_session_confirm():
            path = QFileDialog.getOpenFileName(parent=self, filter='*.lsp',
                                               directory=os.getenv('HOME'))[0]

            if os.path.exists(path):
                self.open_session.emit(path)
                self.file = path
                return True

        return False

    def _new_session_confirm(self):
        confirm = QMessageBox.question(self, 'New session',
                                       'The current session will be lost. '
                                       'Continue?')

        return confirm == QMessageBox.Yes

    def _startup(self):
        if self._new_session_confirm():
            self.new_session.emit()

    def _fullscreen(self, enable):
        if enable:
            self.showFullScreen()
        else:
            self.showMaximized()
