# This file is part of Linux Show Player
#
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

from PyQt5.QtCore import QT_TRANSLATE_NOOP, Qt
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QDialogButtonBox,
    QSizePolicy,
    QHeaderView,
    QTableView,
    QGroupBox,
    QPushButton,
)

from lisp.application import Application
from lisp.cues.cue import CueAction
from lisp.plugins.triggers.triggers_handler import CueTriggers
from lisp.ui.cuelistdialog import CueSelectDialog
from lisp.ui.qdelegates import (
    ComboBoxDelegate,
    CueActionDelegate,
    CueSelectionDelegate,
)
from lisp.ui.qmodels import CueClassRole, SimpleCueListModel
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class TriggersSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "Triggers")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout(self))

        self.cueSelectDialog = CueSelectDialog(cues=Application().cue_model)
        self.triggersModel = TriggersModel()

        self.triggerGroup = QGroupBox(self)
        self.triggerGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.triggerGroup)

        self.triggersView = TriggersView(
            Application().cue_model,
            self.cueSelectDialog,
            parent=self.triggerGroup,
        )
        self.triggersView.setModel(self.triggersModel)
        self.triggerGroup.layout().addWidget(self.triggersView)

        self.dialogButtons = QDialogButtonBox(self.triggerGroup)
        self.dialogButtons.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Minimum
        )
        self.triggerGroup.layout().addWidget(self.dialogButtons)

        self.addButton = QPushButton()
        self.dialogButtons.addButton(
            self.addButton, QDialogButtonBox.ActionRole
        )
        self.addButton.clicked.connect(self._addTrigger)

        self.delButton = QPushButton()
        self.dialogButtons.addButton(
            self.delButton, QDialogButtonBox.ActionRole
        )
        self.delButton.clicked.connect(self._removeCurrentTrigger)

        self.retranlsateUi()

    def retranlsateUi(self):
        self.triggerGroup.setTitle(translate("SettingsPageName", "Triggers"))
        self.addButton.setText(translate("TriggersSettings", "Add"))
        self.delButton.setText(translate("TriggersSettings", "Remove"))

    def enableCheck(self, enabled):
        self.setGroupEnabled(self.triggerGroup, enabled)

    def loadSettings(self, settings):
        # Remove the edited cue from the list of possible targets
        edited_cue = Application().cue_model.get(settings.get("id"))
        if edited_cue:
            self.cueSelectDialog.remove_cue(edited_cue)

        for trigger, targets in settings.get("triggers", {}).items():
            for target, action in targets:
                target = Application().cue_model.get(target)
                if target is not None:
                    self.triggersModel.appendRow(
                        target.__class__, trigger, target.id, CueAction(action)
                    )

    def getSettings(self):
        if self.isGroupEnabled(self.triggerGroup):
            triggers = {}
            for trigger, target, action in self.triggersModel.rows:
                action = action.value

                if trigger not in triggers:
                    triggers[trigger] = []

                # Avoid duplicate
                if (target, action) not in triggers[trigger]:
                    triggers[trigger].append((target, action))

            return {"triggers": triggers}

        return {}

    def _addTrigger(self):
        if self.cueSelectDialog.exec():
            cue = self.cueSelectDialog.selected_cue()
            if cue is not None:
                self.triggersModel.appendRow(
                    cue.__class__,
                    CueTriggers.Started.value,
                    cue.id,
                    cue.CueActions[0],
                )

    def _removeCurrentTrigger(self):
        self.triggersModel.removeRow(self.triggersView.currentIndex().row())


class TriggersView(QTableView):
    def __init__(self, cueModel, cueSelect, **kwargs):
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

        self.delegates = [
            ComboBoxDelegate(
                options=[e.value for e in CueTriggers], tr_context="CueTriggers"
            ),
            CueSelectionDelegate(cueModel, cueSelect),
            CueActionDelegate(),
        ]

        for column, delegate in enumerate(self.delegates):
            self.setItemDelegateForColumn(column, delegate)


class TriggersModel(SimpleCueListModel):
    def __init__(self):
        # NOTE: The model does fixed-indices operations based on this list
        super().__init__(
            [
                translate("TriggersSettings", "Trigger"),
                translate("TriggersSettings", "Cue"),
                translate("TriggersSettings", "Action"),
            ]
        )

        self.rows_cc = []

    def setData(self, index, value, role=Qt.DisplayRole):
        result = super().setData(index, value, role)

        if result and role == CueClassRole:
            if self.rows[index.row()][2] not in value.CueActions:
                self.rows[index.row()][2] = value.CueActions[0]
                self.dataChanged.emit(
                    self.index(index.row(), 2),
                    self.index(index.row(), 2),
                    [Qt.DisplayRole, Qt.EditRole],
                )

        return result
