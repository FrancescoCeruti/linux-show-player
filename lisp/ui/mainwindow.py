# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2018 Francesco Ceruti <ceppofrancy@gmail.com>
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
import os

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QMainWindow, QStatusBar, QMenuBar, QMenu, QAction, \
    qApp, QFileDialog, QMessageBox, QVBoxLayout, QWidget

from lisp.core.actions_handler import MainActionsHandler
from lisp.core.singleton import QSingleton
from lisp.cues.media_cue import MediaCue
from lisp.ui.about import About
from lisp.ui.logging.dialog import LogDialogs
from lisp.ui.logging.handler import LogModelHandler
from lisp.ui.logging.models import log_model_factory
from lisp.ui.logging.status import LogStatusView
from lisp.ui.logging.viewer import LogViewer
from lisp.ui.settings.app_settings import AppSettings
from lisp.ui.ui_utils import translate


class MainWindow(QMainWindow, metaclass=QSingleton):
    new_session = pyqtSignal()
    save_session = pyqtSignal(str)
    open_session = pyqtSignal(str)

    def __init__(self, conf, title='Linux Show Player', **kwargs):
        super().__init__(**kwargs)
        self.setMinimumSize(500, 400)
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(QVBoxLayout())
        self.centralWidget().layout().setContentsMargins(5, 5, 5, 5)

        self._cue_add_menu = {}
        self._title = title

        self.conf = conf
        self.session = None

        # Status Bar
        self.setStatusBar(QStatusBar(self))

        # Changes
        MainActionsHandler.action_done.connect(self._action_done)
        MainActionsHandler.action_undone.connect(self._action_undone)
        MainActionsHandler.action_redone.connect(self._action_redone)

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
        self.newSessionAction = QAction(self)
        self.newSessionAction.triggered.connect(self._new_session)
        self.openSessionAction = QAction(self)
        self.openSessionAction.triggered.connect(self._load_from_file)
        self.saveSessionAction = QAction(self)
        self.saveSessionAction.triggered.connect(self._save)
        self.saveSessionWithName = QAction(self)
        self.saveSessionWithName.triggered.connect(self._save_with_name)
        self.editPreferences = QAction(self)
        self.editPreferences.triggered.connect(self._show_preferences)
        self.fullScreenAction = QAction(self)
        self.fullScreenAction.triggered.connect(self._fullscreen)
        self.fullScreenAction.setCheckable(True)
        self.exitAction = QAction(self)
        self.exitAction.triggered.connect(self._exit)

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
        self.actionUndo.triggered.connect(MainActionsHandler.undo_action)
        self.actionRedo = QAction(self)
        self.actionRedo.triggered.connect(MainActionsHandler.redo_action)
        self.multiEdit = QAction(self)
        self.selectAll = QAction(self)
        self.selectAllMedia = QAction(self)
        self.deselectAll = QAction(self)
        self.invertSelection = QAction(self)

        self.cueSeparator = self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addAction(self.actionRedo)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.selectAll)
        self.menuEdit.addAction(self.selectAllMedia)
        self.menuEdit.addAction(self.deselectAll)
        self.menuEdit.addAction(self.invertSelection)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.multiEdit)

        # menuAbout
        self.actionAbout = QAction(self)
        self.actionAbout.triggered.connect(self._show_about)

        self.actionAbout_Qt = QAction(self)
        self.actionAbout_Qt.triggered.connect(qApp.aboutQt)

        self.menuAbout.addAction(self.actionAbout)
        self.menuAbout.addSeparator()
        self.menuAbout.addAction(self.actionAbout_Qt)

        # Logging model
        self.logModel = log_model_factory(self.conf)

        # Handler to populate the model
        self.logHandler = LogModelHandler(self.logModel)
        logging.getLogger().addHandler(self.logHandler)

        # Logging
        self.logViewer = LogViewer(self.logModel, self.conf, parent=self)

        # Logging status widget
        self.logStatus = LogStatusView(self.logModel)
        self.logStatus.double_clicked.connect(self.logViewer.show)
        self.statusBar().addPermanentWidget(self.logStatus)

        # Logging dialogs for errors
        self.logDialogs = LogDialogs(self.logModel, logging.ERROR)

        # Set component text
        self.retranslateUi()

    def retranslateUi(self):
        self.setWindowTitle(self._title)
        # menuFile
        self.menuFile.setTitle(translate('MainWindow', '&File'))
        self.newSessionAction.setText(translate('MainWindow', 'New session'))
        self.newSessionAction.setShortcut(QKeySequence.New)
        self.openSessionAction.setText(translate('MainWindow', 'Open'))
        self.openSessionAction.setShortcut(QKeySequence.Open)
        self.saveSessionAction.setText(translate('MainWindow', 'Save session'))
        self.saveSessionAction.setShortcut(QKeySequence.Save)
        self.editPreferences.setText(translate('MainWindow', 'Preferences'))
        self.editPreferences.setShortcut(QKeySequence.Preferences)
        self.saveSessionWithName.setText(translate('MainWindow', 'Save as'))
        self.saveSessionWithName.setShortcut(QKeySequence.SaveAs)
        self.fullScreenAction.setText(translate('MainWindow', 'Full Screen'))
        self.fullScreenAction.setShortcut(QKeySequence.FullScreen)
        self.exitAction.setText(translate('MainWindow', 'Exit'))
        # menuEdit
        self.menuEdit.setTitle(translate('MainWindow', '&Edit'))
        self.actionUndo.setText(translate('MainWindow', 'Undo'))
        self.actionUndo.setShortcut(QKeySequence.Undo)
        self.actionRedo.setText(translate('MainWindow', 'Redo'))
        self.actionRedo.setShortcut(QKeySequence.Redo)
        self.selectAll.setText(translate('MainWindow', 'Select all'))
        self.selectAllMedia.setText(
            translate('MainWindow', 'Select all media cues'))
        self.selectAll.setShortcut(QKeySequence.SelectAll)
        self.deselectAll.setText(translate('MainWindow', 'Deselect all'))
        self.deselectAll.setShortcut(translate('MainWindow', 'CTRL+SHIFT+A'))
        self.invertSelection.setText(
            translate('MainWindow', 'Invert selection'))
        self.invertSelection.setShortcut(translate('MainWindow', 'CTRL+I'))
        self.multiEdit.setText(translate('MainWindow', 'Edit selected'))
        self.multiEdit.setShortcut(translate('MainWindow', 'CTRL+SHIFT+E'))
        # menuLayout
        self.menuLayout.setTitle(translate('MainWindow', '&Layout'))
        # menuTools
        self.menuTools.setTitle(translate('MainWindow', '&Tools'))
        self.multiEdit.setText(translate('MainWindow', 'Edit selection'))
        # menuAbout
        self.menuAbout.setTitle(translate('MainWindow', '&About'))
        self.actionAbout.setText(translate('MainWindow', 'About'))
        self.actionAbout_Qt.setText(translate('MainWindow', 'About Qt'))

    def set_session(self, session):
        if self.session is not None:
            layout = self.session.layout
            self.centralWidget().layout().removeWidget(layout)

            self.multiEdit.triggered.disconnect()
            self.selectAll.triggered.disconnect()
            self.selectAllMedia.triggered.disconnect()
            self.deselectAll.triggered.disconnect()
            self.invertSelection.triggered.disconnect()

        self.session = session
        layout = self.session.layout

        self.centralWidget().layout().addWidget(layout)
        layout.show()

        self.multiEdit.triggered.connect(self._edit_selected_cue)
        self.selectAll.triggered.connect(self._select_all)
        self.invertSelection.triggered.connect(self._invert_selection)
        self.deselectAll.triggered.connect(self._deselect_all)
        self.selectAllMedia.triggered.connect(self._select_all_media)

    def closeEvent(self, event):
        self._exit()
        event.ignore()

    def register_cue_menu_action(self, name, function, category='',
                                 shortcut=''):
        """Register a new-cue choice for the edit-menu

        param name: The name for the MenuAction
        param function: The function that add the new cue(s)
        param category: The optional menu where insert the MenuAction
        param shortcut: An optional shortcut for the MenuAction
        """

        action = QAction(self)
        action.setText(translate('MainWindow', name))
        action.triggered.connect(function)
        if shortcut != '':
            action.setShortcut(translate('MainWindow', shortcut))

        if category != '':
            if category not in self._cue_add_menu:
                menu = QMenu(category, self)
                self._cue_add_menu[category] = menu
                self.menuEdit.insertMenu(self.cueSeparator, menu)

            self._cue_add_menu[category].addAction(action)
        else:
            self.menuEdit.insertAction(self.cueSeparator, action)

    def update_window_title(self):
        tile = self._title + ' - ' + self.session.name()
        if not MainActionsHandler.is_saved():
            tile = '*' + tile

        self.setWindowTitle(tile)

    def _action_done(self, action):
        self.update_window_title()

    def _action_undone(self, action):
        self.update_window_title()

    def _action_redone(self, action):
        self.update_window_title()

    def _save(self):
        if self.session.session_file == '':
            self._save_with_name()
        else:
            self.save_session.emit(self.session.session_file)

    def _save_with_name(self):
        filename, ok = QFileDialog.getSaveFileName(
            parent=self, filter='*.lsp', directory=self.session.path())

        if ok:
            if not filename.endswith('.lsp'):
                filename += '.lsp'

            self.save_session.emit(filename)

    def _show_preferences(self):
        prefUi = AppSettings(parent=self)
        prefUi.exec_()

    def _load_from_file(self):
        if self._check_saved():
            path, _ = QFileDialog.getOpenFileName(self, filter='*.lsp',
                                                  directory=os.getenv('HOME'))

            if os.path.exists(path):
                self.open_session.emit(path)

    def _new_session(self):
        if self._check_saved():
            self.new_session.emit()

    def _check_saved(self):
        if not MainActionsHandler.is_saved():
            msgBox = QMessageBox(self)
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setWindowTitle(translate('MainWindow', 'Close session'))
            msgBox.setText(
                translate('MainWindow', 'The current session is not saved.'))
            msgBox.setInformativeText(
                translate('MainWindow', 'Discard the changes?'))
            msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard |
                                      QMessageBox.Cancel)
            msgBox.setDefaultButton(QMessageBox.Save)

            result = msgBox.exec_()
            if result == QMessageBox.Cancel:
                return False
            elif result == QMessageBox.Save:
                self._save()

        return True

    def _fullscreen(self, enable):
        if enable:
            self.showFullScreen()
        else:
            self.showMaximized()

    def _show_about(self):
        About(self).show()

    def _exit(self):
        if self._check_saved():
            qApp.quit()

    def _edit_selected_cue(self):
        self.session.layout.edit_selected_cues()

    def _select_all(self):
        self.session.layout.select_all()

    def _invert_selection(self):
        self.session.layout.invert_selection()

    def _deselect_all(self):
        self.session.layout.deselect_all()

    def _select_all_media(self):
        self.session.layout.select_all(cue_class=MediaCue)