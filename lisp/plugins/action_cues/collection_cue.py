# This file is part of Linux Show Player
#
# Copyright 2018 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QSizePolicy,
    QDialogButtonBox,
    QDialog,
    QAbstractItemView,
    QHeaderView,
    QTableView,
)

from lisp.application import Application
from lisp.core.properties import Property
from lisp.cues.cue import Cue, CueAction
from lisp.ui.cuelistdialog import CueSelectDialog
from lisp.ui.qdelegates import CueActionDelegate, CueSelectionDelegate
from lisp.ui.qmodels import CueClassRole, SimpleCueListModel
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class CollectionCue(Cue):
    Name = QT_TRANSLATE_NOOP("CueName", "Collection Cue")
    Category = QT_TRANSLATE_NOOP("CueCategory", "Action cues")

    targets = Property(default=[])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = translate("CueName", self.Name)

    def __start__(self, fade=False):
        for target_id, action in self.targets:
            cue = Application().cue_model.get(target_id)
            if cue is not self:
                cue.execute(action=CueAction[action])

        return False


class CollectionCueSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "Edit Collection")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout(self))

        self.cue_dialog = CueSelectDialog(
            cues=Application().cue_model,
            selection_mode=QAbstractItemView.ExtendedSelection,
        )

        self.collectionModel = CollectionModel()
        self.collectionView = CollectionView(self.cue_dialog, parent=self)
        self.collectionView.setModel(self.collectionModel)
        self.collectionView.setAlternatingRowColors(True)
        self.layout().addWidget(self.collectionView)

        # Buttons
        self.dialogButtons = QDialogButtonBox(self)
        self.dialogButtons.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Minimum
        )
        self.layout().addWidget(self.dialogButtons)

        self.addButton = self.dialogButtons.addButton(
            translate("CollectionCue", "Add"), QDialogButtonBox.ActionRole
        )
        self.addButton.clicked.connect(self._add_dialog)

        self.delButton = self.dialogButtons.addButton(
            translate("CollectionCue", "Remove"), QDialogButtonBox.ActionRole
        )
        self.delButton.clicked.connect(self._remove_selected)

    def loadSettings(self, settings):
        for target_id, action in settings.get("targets", []):
            target = Application().cue_model.get(target_id)
            if target is not None:
                self._add_cue(target, CueAction(action))

    def getSettings(self):
        targets = []
        for target_id, action in self.collectionModel.rows:
            targets.append((target_id, action.value))

        return {"targets": targets}

    def _add_cue(self, cue, action):
        self.collectionModel.appendRow(cue.__class__, cue.id, action)
        self.cue_dialog.remove_cue(cue)

    def _add_dialog(self):
        if self.cue_dialog.exec() == QDialog.Accepted:
            for target in self.cue_dialog.selected_cues():
                self._add_cue(target, target.CueActions[0])

    def _remove_selected(self):
        row = self.collectionView.currentIndex().row()
        cue_id = self.collectionModel.rows[row][0]

        self.collectionModel.removeRow(row)
        self.cue_dialog.add_cue(Application().cue_model.get(cue_id))


class CollectionView(QTableView):
    def __init__(self, cue_select, **kwargs):
        super().__init__(**kwargs)

        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)

        self.setShowGrid(False)
        self.setAlternatingRowColors(True)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setHighlightSections(False)

        self.verticalHeader().sectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(26)
        self.verticalHeader().setHighlightSections(False)

        self.delegates = [CueSelectionDelegate(cue_select), CueActionDelegate()]

        for column, delegate in enumerate(self.delegates):
            self.setItemDelegateForColumn(column, delegate)


class CollectionModel(SimpleCueListModel):
    def __init__(self):
        # NOTE: The model does fixed-indices operations based on this list
        super().__init__(
            [
                translate("CollectionCue", "Cue"),
                translate("CollectionCue", "Action"),
            ]
        )

    def setData(self, index, value, role=Qt.DisplayRole):
        result = super().setData(index, value, role)

        if result and role == CueClassRole:
            if self.rows[index.row()][1] not in value.CueActions:
                self.rows[index.row()][1] = value.CueActions[0]
                self.dataChanged.emit(
                    self.index(index.row(), 1),
                    self.index(index.row(), 1),
                    [Qt.DisplayRole, Qt.EditRole],
                )

        return result


CueSettingsRegistry().add(CollectionCueSettings, CollectionCue)
