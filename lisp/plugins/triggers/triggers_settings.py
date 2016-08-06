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

from PyQt5.QtCore import QEvent, QT_TRANSLATE_NOOP, Qt
from PyQt5.QtWidgets import QVBoxLayout, QDialogButtonBox, QSizePolicy, \
    QDialog, QHeaderView, QTableView

from lisp.application import Application
from lisp.cues.cue import Cue, CueAction
from lisp.plugins.triggers.triggers_handler import CueTriggers
from lisp.ui.cuelistdialog import CueListDialog
from lisp.ui.qdelegates import ComboBoxDelegate, CueActionDelegate, \
    LabelDelegate
from lisp.ui.qmodels import SimpleTableModel, CueClassRole
from lisp.ui.settings.settings_page import SettingsPage
from lisp.utils.util import translate


class TriggersSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'Triggers')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout(self))
        self.layout().setAlignment(Qt.AlignTop)

        self.cue_select = CueListDialog(cues=Application().cue_model)

        self.triggersModel = TriggersModel()

        self.triggersView = TriggersView(self.cue_select, parent=self)
        self.triggersView.setModel(self.triggersModel)
        self.layout().addWidget(self.triggersView)

        self.dialogButtons = QDialogButtonBox(self)
        self.dialogButtons.setSizePolicy(QSizePolicy.Minimum,
                                         QSizePolicy.Minimum)
        self.layout().addWidget(self.dialogButtons)

        self.addButton = self.dialogButtons.addButton(
            translate('TriggersSettings', 'Add'), QDialogButtonBox.ActionRole)
        self.addButton.clicked.connect(self._add_trigger)

        self.delButton = self.dialogButtons.addButton(
            translate('TriggersSettings', 'Remove'),
            QDialogButtonBox.ActionRole)
        self.delButton.clicked.connect(self._remove_trigger)

    def _add_trigger(self):
        if self.cue_select.exec():
            cue = self.cue_select.selected_cue()
            if cue is not None:
                self.triggersModel.appendRow(cue.__class__,
                                             CueTriggers.Started.value,
                                             cue.id,
                                             cue.CueActions[0])

    def _remove_trigger(self):
        self.triggersModel.removeRow(self.triggersView.currentIndex().row())

    def load_settings(self, settings):
        # Remove the edited cue from the list of possible targets
        edited_cue = Application().cue_model.get(settings.get('id'))
        if edited_cue:
            self.cue_select.remove_cue(edited_cue)

        for trigger, targets in settings.get('triggers', {}).items():
            for target, action in targets:
                target = Application().cue_model.get(target)
                if target is not None:
                    self.triggersModel.appendRow(target.__class__, trigger,
                                                 target.id, CueAction(action))

    def get_settings(self):
        triggers = {}
        for trigger, target, action in self.triggersModel.rows:
            action = action.value

            if trigger not in triggers:
                triggers[trigger] = []

            # Avoid duplicate
            if (target, action) not in triggers[trigger]:
                triggers[trigger].append((target, action))

        return {'triggers': triggers}


class TriggersView(QTableView):
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

        self.delegates = [
            ComboBoxDelegate(options=[e.value for e in CueTriggers],
                             tr_context='CueTriggers'),
            CueSelectionDelegate(cue_select),
            CueActionDelegate()
        ]

        for column, delegate in enumerate(self.delegates):
            self.setItemDelegateForColumn(column, delegate)


class CueSelectionDelegate(LabelDelegate):
    def __init__(self, cue_select, **kwargs):
        super().__init__(**kwargs)
        self.cue_select = cue_select

    def _text(self, painter, option, index):
        cue = Application().cue_model.get(index.data())
        if cue is not None:
            return '{} | {}'.format(cue.index, cue.name)

        return 'UNDEF'

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseButtonDblClick:
            if self.cue_select.exec_() == QDialog.Accepted:
                cue = self.cue_select.selected_cue()
                if cue is not None:
                    model.setData(index, cue.id, Qt.EditRole)
                    model.setData(index, cue.__class__, CueClassRole)
            return True

        return super().editorEvent(event, model, option, index)


class TriggersModel(SimpleTableModel):
    def __init__(self):
        # NOTE: The model does fixed-indices operations based on this list
        super().__init__([translate('TriggersSettings', 'Trigger'),
                          translate('TriggersSettings', 'Cue'),
                          translate('TriggersSettings', 'Action')])

        self.rows_cc = []

    def appendRow(self, cue_class, *values):
        self.rows_cc.append(cue_class)
        super().appendRow(*values)

    def removeRow(self, row, parent=None):
        if super().removeRow(row):
            self.rows_cc.pop(row)

    def data(self, index, role=Qt.DisplayRole):
        if role == CueClassRole and index.isValid:
            return self.rows_cc[index.row()]

        return super().data(index, role)

    def setData(self, index, value, role=Qt.DisplayRole):
        if role == CueClassRole and index.isValid():
            if issubclass(value, Cue):
                self.rows_cc[index.row()] = value

                if self.rows[index.row()][2] not in value.CueActions:
                    self.rows[index.row()][2] = value.CueActions[0]
                    self.dataChanged.emit(self.index(index.row(), 2),
                                          self.index(index.row(), 2),
                                          [Qt.DisplayRole, Qt.EditRole])

                return True

            return False

        return super().setData(index, value, role)

    def flags(self, index):
        return super().flags(index)
