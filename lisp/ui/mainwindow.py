# This file is part of Linux Show Player
#
# Copyright 2019 Francesco Ceruti <ceppofrancy@gmail.com>
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
from PyQt5.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QMenuBar,
    QMenu,
    QAction,
    qApp,
    QFileDialog,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)
from functools import partial

from lisp.core.actions_handler import MainActionsHandler
from lisp.core.singleton import QSingleton
from lisp.cues.cue_factory import CueFactory
from lisp.cues.media_cue import MediaCue
from lisp.ui.about import About
from lisp.ui.logging.dialog import LogDialogs
from lisp.ui.logging.handler import LogModelHandler
from lisp.ui.logging.models import log_model_factory
from lisp.ui.logging.status import LogStatusView
from lisp.ui.logging.viewer import LogViewer
from lisp.ui.settings.app_configuration import AppConfigurationDialog
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow, metaclass=QSingleton):
    new_session = pyqtSignal()
    save_session = pyqtSignal(str)
    open_session = pyqtSignal(str)

    def __init__(self, conf, title="Linux Show Player", **kwargs):
        super().__init__(**kwargs)
        self.setMinimumSize(500, 400)
        self.setGeometry(qApp.desktop().availableGeometry(self))
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(QVBoxLayout())
        self.centralWidget().layout().setContentsMargins(5, 5, 5, 5)

        self.__cueSubMenus = {}
        self._title = title

        self.conf = conf
        self.session = None

        # Status Bar
        self.setStatusBar(QStatusBar(self))

        # Changes
        MainActionsHandler.action_done.connect(self.updateWindowTitle)
        MainActionsHandler.action_undone.connect(self.updateWindowTitle)
        MainActionsHandler.action_redone.connect(self.updateWindowTitle)

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
        self.newSessionAction.triggered.connect(self.__newSession)
        self.openSessionAction = QAction(self)
        self.openSessionAction.triggered.connect(self.__openSession)
        self.saveSessionAction = QAction(self)
        self.saveSessionAction.triggered.connect(self.__saveSession)
        self.saveSessionWithName = QAction(self)
        self.saveSessionWithName.triggered.connect(self.__saveWithName)
        self.editPreferences = QAction(self)
        self.editPreferences.triggered.connect(self.__onEditPreferences)
        self.fullScreenAction = QAction(self)
        self.fullScreenAction.triggered.connect(self.setFullScreen)
        self.fullScreenAction.setCheckable(True)
        self.exitAction = QAction(self)
        self.exitAction.triggered.connect(self.close)

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
        self.multiEdit.triggered.connect(self.__editSelectedCues)
        self.selectAll = QAction(self)
        self.selectAll.triggered.connect(self.__layoutSelectAll)
        self.selectAllMedia = QAction(self)
        self.selectAllMedia.triggered.connect(self.__layoutSelectAllMediaCues)
        self.deselectAll = QAction(self)
        self.deselectAll.triggered.connect(self._layoutDeselectAll)
        self.invertSelection = QAction(self)
        self.invertSelection.triggered.connect(self.__layoutInvertSelection)

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
        self.actionAbout.triggered.connect(self.__about)

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
        self.logViewer = LogViewer(self.logModel, self.conf)

        # Logging status widget
        self.logStatus = LogStatusView(self.logModel)
        self.logStatus.double_clicked.connect(self.logViewer.showMaximized)
        self.statusBar().addPermanentWidget(self.logStatus)

        # Logging dialogs for errors
        self.logDialogs = LogDialogs(
            self.logModel, level=logging.ERROR, parent=self
        )

        # Set component text
        self.retranslateUi()

    def retranslateUi(self):
        self.setWindowTitle(self._title)
        # menuFile
        self.menuFile.setTitle(translate("MainWindow", "&File"))
        self.newSessionAction.setText(translate("MainWindow", "New session"))
        self.newSessionAction.setShortcut(QKeySequence.New)
        self.openSessionAction.setText(translate("MainWindow", "Open"))
        self.openSessionAction.setShortcut(QKeySequence.Open)
        self.saveSessionAction.setText(translate("MainWindow", "Save session"))
        self.saveSessionAction.setShortcut(QKeySequence.Save)
        self.editPreferences.setText(translate("MainWindow", "Preferences"))
        self.editPreferences.setShortcut(QKeySequence.Preferences)
        self.saveSessionWithName.setText(translate("MainWindow", "Save as"))
        self.saveSessionWithName.setShortcut(QKeySequence.SaveAs)
        self.fullScreenAction.setText(translate("MainWindow", "Full Screen"))
        self.fullScreenAction.setShortcut(QKeySequence.FullScreen)
        self.exitAction.setText(translate("MainWindow", "Exit"))
        # menuEdit
        self.menuEdit.setTitle(translate("MainWindow", "&Edit"))
        self.actionUndo.setText(translate("MainWindow", "Undo"))
        self.actionUndo.setShortcut(QKeySequence.Undo)
        self.actionRedo.setText(translate("MainWindow", "Redo"))
        self.actionRedo.setShortcut(QKeySequence.Redo)
        self.selectAll.setText(translate("MainWindow", "Select all"))
        self.selectAllMedia.setText(
            translate("MainWindow", "Select all media cues")
        )
        self.selectAll.setShortcut(QKeySequence.SelectAll)
        self.deselectAll.setText(translate("MainWindow", "Deselect all"))
        self.deselectAll.setShortcut(translate("MainWindow", "CTRL+SHIFT+A"))
        self.invertSelection.setText(
            translate("MainWindow", "Invert selection")
        )
        self.invertSelection.setShortcut(translate("MainWindow", "CTRL+I"))
        self.multiEdit.setText(translate("MainWindow", "Edit selected"))
        self.multiEdit.setShortcut(translate("MainWindow", "CTRL+SHIFT+E"))
        # menuLayout
        self.menuLayout.setTitle(translate("MainWindow", "&Layout"))
        # menuTools
        self.menuTools.setTitle(translate("MainWindow", "&Tools"))
        self.multiEdit.setText(translate("MainWindow", "Edit selection"))
        # menuAbout
        self.menuAbout.setTitle(translate("MainWindow", "&About"))
        self.actionAbout.setText(translate("MainWindow", "About"))
        self.actionAbout_Qt.setText(translate("MainWindow", "About Qt"))

    def setSession(self, session):
        if self.session is not None:
            self.centralWidget().layout().removeWidget(
                self.session.layout.view()
            )
            # Remove ownership, this allow the widget to be deleted
            self.session.layout.view().setParent(None)

        self.session = session
        self.session.layout.view().show()
        self.centralWidget().layout().addWidget(self.session.layout.view())

    def closeEvent(self, event):
        if self.__checkSessionSaved():
            qApp.quit()
            event.accept()
        else:
            event.ignore()

    def registerCueMenu(self, name, function, category="", shortcut=""):
        """Register a new-cue choice for the edit-menu

        param name: The name for the MenuAction
        param function: The function that add the new cue(s)
        param category: The optional menu where insert the MenuAction
        param shortcut: An optional shortcut for the MenuAction
        """

        action = QAction(self)
        action.setText(translate("CueName", name))
        action.triggered.connect(function)
        if shortcut != "":
            action.setShortcut(translate("CueCategory", shortcut))

        if category:
            if category not in self.__cueSubMenus:
                subMenu = QMenu(category, self)
                self.__cueSubMenus[category] = subMenu
                self.menuEdit.insertMenu(self.cueSeparator, subMenu)

            self.__cueSubMenus[category].addAction(action)
        else:
            self.menuEdit.insertAction(self.cueSeparator, action)

        logger.debug(
            translate("MainWindowDebug", 'Registered cue menu: "{}"').format(
                name
            )
        )

    def registerSimpleCueMenu(self, cueClass, category=""):
        self.registerCueMenu(
            translate("CueName", cueClass.Name),
            partial(self.__simpleCueInsert, cueClass),
            category or translate("CueCategory", "Misc cues"),
        )

    def updateWindowTitle(self):
        tile = self._title + " - " + self.session.name()
        if not MainActionsHandler.is_saved():
            tile = "*" + tile

        self.setWindowTitle(tile)

    def getOpenSessionFile(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            filter="*.lsp",
            directory=self.conf.get("session.last_dir", os.getenv("HOME")),
        )

        if os.path.exists(path):
            self.conf.set("session.last_dir", os.path.dirname(path))
            self.conf.write()

            return path

    def getSaveSessionFile(self):
        if self.session.session_file:
            session_dir = self.session.dir()
        else:
            session_dir = self.conf.get("session.last_dir", os.getenv("HOME"))

        filename, accepted = QFileDialog.getSaveFileName(
            parent=self, filter="*.lsp", directory=session_dir
        )

        if accepted:
            if not filename.endswith(".lsp"):
                filename += ".lsp"

            return filename

    def setFullScreen(self, enable):
        if enable:
            self.showFullScreen()
        else:
            self.showMaximized()

    def __simpleCueInsert(self, cueClass):
        try:
            cue = CueFactory.create_cue(cueClass.__name__)

            # Get the (last) index of the current selection
            layout_selection = list(self.session.layout.selected_cues())
            if layout_selection:
                cue.index = layout_selection[-1].index + 1

            self.session.cue_model.add(cue)
        except Exception:
            logger.exception(
                translate("MainWindowError", "Cannot create cue {}").format(
                    cueClass.__name__
                )
            )

    def __onEditPreferences(self):
        prefUi = AppConfigurationDialog(parent=self)
        prefUi.exec()

    def __editSelectedCues(self):
        self.session.layout.edit_cues(list(self.session.layout.selected_cues()))

    def __layoutSelectAll(self):
        self.session.layout.select_all()

    def __layoutInvertSelection(self):
        self.session.layout.invert_selection()

    def _layoutDeselectAll(self):
        self.session.layout.deselect_all()

    def __layoutSelectAllMediaCues(self):
        self.session.layout.select_all(cue_type=MediaCue)

    def __saveSession(self):
        if self.session.session_file:
            self.save_session.emit(self.session.session_file)
            return True
        else:
            return self.__saveWithName()

    def __saveWithName(self):
        path = self.getSaveSessionFile()

        if path is not None:
            self.save_session.emit(path)
            return True

        return False

    def __openSession(self):
        path = self.getOpenSessionFile()

        if path is not None:
            self.open_session.emit(path)

    def __newSession(self):
        if self.__checkSessionSaved():
            self.new_session.emit()

    def __checkSessionSaved(self):
        if not MainActionsHandler.is_saved():
            saveMessageBox = QMessageBox(
                QMessageBox.Warning,
                translate("MainWindow", "Close session"),
                translate(
                    "MainWindow",
                    "The current session contains changes that have not been saved.",
                ),
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                self,
            )
            saveMessageBox.setInformativeText(
                translate("MainWindow", "Do you want to save them now?")
            )
            saveMessageBox.setDefaultButton(QMessageBox.Save)

            choice = saveMessageBox.exec()
            if choice == QMessageBox.Save:
                return self.__saveSession()
            elif choice == QMessageBox.Cancel:
                return False

        return True

    def __about(self):
        About(self).show()
