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

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QVBoxLayout, QSizePolicy, QListWidget, \
    QDialogButtonBox, QDialog, QAbstractItemView, QWidget, QHBoxLayout, \
    QPushButton, QComboBox, QListWidgetItem

from lisp.application import Application
from lisp.core.decorators import async
from lisp.core.has_properties import Property
from lisp.cues.cue import Cue, CueState, CueAction
from lisp.layouts.cue_layout import CueLayout
from lisp.ui.cuelistdialog import CueListDialog
from lisp.ui.settings.section import SettingsSection


class CollectionCue(Cue):
    Name = 'Collection Cue'

    targets = Property(default=[])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = self.Name

    @Cue.state.setter
    def state(self):
        return CueState.Stop

    def __start__(self):
        for target_id, action in self.targets:
            cue = Application().cue_model.get(target_id)
            if cue is not None and cue is not self:
                cue.execute(action=CueAction[action])


class CollectionCueSettings(SettingsSection):
    Name = 'Edit Collection'

    def __init__(self, size, cue=None, parent=None):
        super().__init__(size, cue=cue, parent=parent)

        self.setLayout(QVBoxLayout(self))

        self.cuesWidget = QListWidget(self)
        self.cuesWidget.setAlternatingRowColors(True)
        self.layout().addWidget(self.cuesWidget)

        # Buttons
        self.dialogButtons = QDialogButtonBox(self)
        self.dialogButtons.setSizePolicy(QSizePolicy.Minimum,
                                         QSizePolicy.Minimum)
        self.layout().addWidget(self.dialogButtons)

        self.addButton = self.dialogButtons.addButton('Add', QDialogButtonBox.ActionRole)
        self.addButton.clicked.connect(self._add_dialog)

        self.delButton = self.dialogButtons.addButton('Remove', QDialogButtonBox.ActionRole)
        self.delButton.clicked.connect(self._remove_selected)

        self.cue_dialog = CueListDialog(cues=Application().cue_model)
        self.cue_dialog.list.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def set_configuration(self, conf):
        for target_id, action in conf.get('targets', []):
            target = Application().cue_model.get(target_id)
            if target is not None:
                self._add_cue(target, action)

    def get_configuration(self):
        targets = []
        for n in range(self.cuesWidget.count()):
            widget = self.cuesWidget.itemWidget(self.cuesWidget.item(n))
            target_id, action = widget.get_target()
            targets.append((target_id, action))

        return {'targets': targets}

    def _add_cue(self, cue, action):
        item = QListWidgetItem()
        item.setSizeHint(QSize(200, 30))

        widget = CueItemWidget(cue, action, self.cue_dialog)

        self.cuesWidget.addItem(item)
        self.cuesWidget.setItemWidget(item, widget)
        self.cue_dialog.remove_cue(cue)

    def _add_dialog(self):
        if self.cue_dialog.exec_() == QDialog.Accepted:
            for target in self.cue_dialog.selected_cues():
                self._add_cue(target, tuple(target.CueAction)[0].name)

    def _remove_selected(self):
        cue = self.cuesWidget.itemWidget(self.cuesWidget.currentItem()).target

        self.cuesWidget.takeItem(self.cuesWidget.currentRow())
        self.cue_dialog.add_cue(cue)


class CueItemWidget(QWidget):
    def __init__(self, target, action, cue_dialog, **kwargs):
        super().__init__(**kwargs)

        self.target = target
        self.cue_dialog = cue_dialog

        self.setLayout(QHBoxLayout(self))
        self.layout().setContentsMargins(2, 1, 2, 1)

        self.selectButton = QPushButton(self)
        self.selectButton.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.selectButton.setText(target.name)
        self.selectButton.setToolTip(target.name)
        self.selectButton.clicked.connect(self.select_target)
        self.layout().addWidget(self.selectButton)

        self.targetActionsCombo = QComboBox(self)
        self.targetActionsCombo.addItems([a.name for a in CueAction])
        self.targetActionsCombo.setCurrentText(CueAction[action].name)
        self.layout().addWidget(self.targetActionsCombo)

        self.layout().setStretch(0, 3)
        self.layout().setStretch(1, 1)

    def get_target(self):
        return self.target.id, self.targetActionsCombo.currentText()

    def select_target(self):
        if self.cue_dialog.exec_() == QDialog.Accepted:
            self.target = self.cue_dialog.selected_cues()[0]
            self.selectButton.setText(self.target.name)
            self.selectButton.setToolTip(self.target.name)


CueLayout.add_settings_section(CollectionCueSettings, CollectionCue)
