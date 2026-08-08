from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QKeySequence

from lisp.core.plugin import Plugin
from lisp.ui.ui_utils import translate
from .dialog import CueSearchDialog


class CueSearch(Plugin):
    Name = "Cue Search"
    Description = "Advanced dialog to search and trigger cues"
    Authors = ("Francesco Ceruti", "Tom Mansion")

    def __init__(self, app):
        super().__init__(app)

        # Entry in mainWindow menu
        self.menuAction = QAction(self.app.window)
        self.menuAction.setText(translate("CueSearch", "Find cues"))
        self.menuAction.setShortcut(QKeySequence.Find)
        self.menuAction.triggered.connect(self.__open_dialog)

        self.app.window.menuTools.addAction(self.menuAction)

    def __open_dialog(self):
        CueSearchDialog(
            self.app, CueSearch.Config, parent=self.app.window
        ).show()
