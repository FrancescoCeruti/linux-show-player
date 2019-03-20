# This file is part of Linux Show Player
#
# Copyright 2016-2017 Aurelien Cibrario <aurelien.cibrario@gmail.com>
# Copyright 2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtWidgets import QAction, QDialog
from lisp.core.actions_handler import MainActionsHandler

from lisp.core.plugin import Plugin
from lisp.plugins.rename_cues.rename_action import RenameCueAction
from lisp.ui.ui_utils import translate
from .rename_ui import RenameUi


class RenameCues(Plugin):
    Name = "RenameCues"
    Authors = ("Aurelien Cibrario",)
    Description = "Provide a dialog for batch renaming of cues"

    def __init__(self, app):
        super().__init__(app)

        # Entry in mainWindow menu
        self.menuAction = QAction(
            translate("RenameCues", "Rename Cues"), self.app.window
        )
        self.menuAction.triggered.connect(self.rename)

        self.app.window.menuTools.addAction(self.menuAction)

    def rename(self):
        # Test if some cues are selected, else select all cues
        selected_cues = list(self.app.layout.selected_cues())
        if not selected_cues:
            # TODO : implement dialog box if/when QSettings is implemented
            # the dialog should inform the user that rename_module load only selected cues if needed
            # but it will bother more than being useful if we can't provide a "Don't show again"
            # Could be provided by QErrorMessage if QSettings is supported
            selected_cues = list(self.app.cue_model)

        # Initiate rename windows
        renameUi = RenameUi(self.app.window, selected_cues)

        renameUi.exec()

        if renameUi.result() == QDialog.Accepted:
            MainActionsHandler.do_action(
                RenameCueAction(self.app, renameUi.cues_list)
            )

    def terminate(self):
        self.app.window.menuTools.removeAction(self.menuAction)
