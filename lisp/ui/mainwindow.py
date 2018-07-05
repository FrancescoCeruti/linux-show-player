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
from functools import partial

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QT_TRANSLATE_NOOP
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
    QFrame,
    QHBoxLayout,
    QSizePolicy,
)

from lisp.command.layout import LayoutAutoInsertCuesCommand
from lisp.core.singleton import QSingleton
from lisp.cues.media_cue import MediaCue
from lisp.ui.about import About
from lisp.ui.logging.dialog import LogDialogs
from lisp.ui.logging.handler import LogModelHandler
from lisp.ui.logging.models import create_log_model
from lisp.ui.logging.status import LogStatusIcon, LogMessageWidget
from lisp.ui.logging.viewer import LogViewer
from lisp.ui.settings.app_configuration import AppConfigurationDialog
from lisp.ui.settings.session_configuration import SessionConfigurationDialog
from lisp.ui.ui_utils import translate
from lisp.ui.widgets import DigitalLabelClock

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow, metaclass=QSingleton):
    new_session = pyqtSignal()
    save_session = pyqtSignal(str)
    open_session = pyqtSignal(str)

    def __init__(self, app, title="Linux Show Player", **kwargs):
        """:type app: lisp.application.Application"""
        super().__init__(**kwargs)
        self.setMinimumSize(500, 400)
        self.setGeometry(qApp.desktop().availableGeometry(self))
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(QVBoxLayout())
        self.centralWidget().layout().setContentsMargins(5, 5, 5, 5)
        self.setStatusBar(QStatusBar(self))

        self._app = app
        self._title = title
        self._cueSubMenus = {}

        # Session change
        self._app.session_created.connect(self.__sessionCreated)
        self._app.session_before_finalize.connect(self.__beforeSessionFinalize)
        self._app.session_loaded.connect(self.updateWindowTitle)

        # Changes
        self._app.commands_stack.done.connect(self.updateWindowTitle)
        self._app.commands_stack.saved.connect(self.updateWindowTitle)
        self._app.commands_stack.undone.connect(self.updateWindowTitle)
        self._app.commands_stack.redone.connect(self.updateWindowTitle)

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
        self.actionUndo.triggered.connect(self._app.commands_stack.undo_last)
        self.actionRedo = QAction(self)
        self.actionRedo.triggered.connect(self._app.commands_stack.redo_last)
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

        # menuTools
        self.sessionPreferences = QAction(self)
        self.sessionPreferences.triggered.connect(self._show_session_preferences)
        self.menuTools.addAction(self.sessionPreferences)
        self.menuTools.addSeparator()

        # menuAbout
        self.actionAbout = QAction(self)
        self.actionAbout.triggered.connect(self.__about)

        self.actionAbout_Qt = QAction(self)
        self.actionAbout_Qt.triggered.connect(qApp.aboutQt)

        self.menuAbout.addAction(self.actionAbout)
        self.menuAbout.addSeparator()
        self.menuAbout.addAction(self.actionAbout_Qt)

        # Logging
        self.logModel = create_log_model(self._app.conf)
        self.logHandler = LogModelHandler(self.logModel)
        self.logViewer = LogViewer(self.logModel, self._app.conf)
        self.logDialogs = LogDialogs(
            self.logModel, level=logging.ERROR, parent=self
        )
        logging.getLogger().addHandler(self.logHandler)

        # Status bar
        self.statusBar().addPermanentWidget(MainStatusBar(self), 1)

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
        self.exitAction.setShortcut(QKeySequence.Quit)
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
        self.sessionPreferences.setText(translate("MainWindow", "Session Preferences"))
        # menuAbout
        self.menuAbout.setTitle(translate("MainWindow", "&About"))
        self.actionAbout.setText(translate("MainWindow", "About"))
        self.actionAbout_Qt.setText(translate("MainWindow", "About Qt"))

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
            if category not in self._cueSubMenus:
                subMenu = QMenu(translate("CueCategory", category), self)
                self._cueSubMenus[category] = subMenu
                self.menuEdit.insertMenu(self.cueSeparator, subMenu)

            self._cueSubMenus[category].addAction(action)
        else:
            self.menuEdit.insertAction(self.cueSeparator, action)

        logger.debug(
            translate("MainWindowDebug", 'Registered cue menu: "{}"').format(
                name
            )
        )

    def registerSimpleCueMenu(self, cueClass, category=""):
        self.registerCueMenu(
            cueClass.Name,
            partial(self.__simpleCueInsert, cueClass),
            category or QT_TRANSLATE_NOOP("CueCategory", "Misc cues"),
        )

    def updateWindowTitle(self):
        tile = self._title + " - " + self._app.session.name()
        if not self._app.commands_stack.is_saved():
            tile = "*" + tile

        self.setWindowTitle(tile)

    def getOpenSessionFile(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            filter="*.lsp",
            directory=self._app.conf.get("session.lastPath", os.getenv("HOME")),
        )

        if os.path.exists(path):
            self._app.conf.set("session.lastPath", os.path.dirname(path))
            self._app.conf.write()

            return path

    def getSaveSessionFile(self):
        if self._app.session.session_file:
            directory = self._app.session.dir()
        else:
            directory = self._app.conf.get(
                "session.lastPath", os.getenv("HOME")
            )

        path, _ = QFileDialog.getSaveFileName(
            parent=self, filter="*.lsp", directory=directory
        )

        if path:
            if not path.endswith(".lsp"):
                path += ".lsp"

            return path

    def setFullScreen(self, enable):
        if enable:
            self.showFullScreen()
        else:
            self.showMaximized()

    def closeEvent(self, event):
        if self.__checkSessionSaved():
            qApp.quit()
            event.accept()
        else:
            event.ignore()

    def _show_session_preferences(self):
        prefUi = SessionConfigurationDialog(parent=self)
        prefUi.exec_()

    def __beforeSessionFinalize(self):
        self.centralWidget().layout().removeWidget(
            self._app.session.layout.view
        )
        # Remove ownership, this allow the widget to be deleted
        self._app.session.layout.view.setParent(None)

    def __sessionCreated(self):
        self._app.session.layout.view.show()
        self.centralWidget().layout().addWidget(self._app.session.layout.view)
        self.updateWindowTitle()

    def __simpleCueInsert(self, cueClass):
        try:
            self._app.commands_stack.do(
                LayoutAutoInsertCuesCommand(
                    self._app.session.layout,
                    self._app.cue_factory.create_cue(cueClass.__name__),
                )
            )
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
        self._app.session.layout.edit_cues(
            list(self._app.session.layout.selected_cues())
        )

    def __layoutSelectAll(self):
        self._app.session.layout.select_all()

    def __layoutInvertSelection(self):
        self._app.session.layout.invert_selection()

    def _layoutDeselectAll(self):
        self._app.session.layout.deselect_all()

    def __layoutSelectAllMediaCues(self):
        self._app.session.layout.select_all(cue_type=MediaCue)

    def __saveSession(self):
        if self._app.session.session_file:
            self.save_session.emit(self._app.session.session_file)
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
        if not self._app.commands_stack.is_saved():
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


class MainStatusBar(QWidget):
    def __init__(self, mainWindow):
        super().__init__(parent=mainWindow.statusBar())
        self.setLayout(QHBoxLayout())
        self.layout().setSpacing(10)
        self.layout().setContentsMargins(5, 5, 5, 5)

        # Clock
        self.clock = DigitalLabelClock(parent=self)
        self.clock.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.addWidget(self.clock)
        # ---------
        self.addDivider()
        # Logging Messages
        self.logMessage = LogMessageWidget(mainWindow.logModel, parent=self)
        self.addWidget(self.logMessage)
        # ---------
        self.addDivider()
        # Logging StatusIcon
        self.logStatus = LogStatusIcon(mainWindow.logModel, parent=self)
        self.logStatus.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.logStatus.double_clicked.connect(
            mainWindow.logViewer.showMaximized
        )
        self.addWidget(self.logStatus)

    def addWidget(self, widget):
        self.layout().addWidget(widget)

    def addDivider(self):
        divider = QFrame(self)
        divider.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        divider.setFrameShape(QFrame.VLine)
        divider.setFrameShadow(QFrame.Sunken)
        self.addWidget(divider)
