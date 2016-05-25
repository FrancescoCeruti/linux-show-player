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

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QVBoxLayout, QListWidget, QDialogButtonBox, \
    QSizePolicy, QListWidgetItem, QDialog, QWidget, QHBoxLayout, QComboBox, \
    QPushButton

from lisp.application import Application
from lisp.cues.cue import CueAction
from lisp.plugins.triggers.triggers_handler import CueTriggers
from lisp.ui.cuelistdialog import CueListDialog
from lisp.ui.settings.settings_page import SettingsPage


class TriggersSettings(SettingsPage):

    Name = 'Triggers'
    PluginInstance = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout(self))

        self.triggersWidget = QListWidget(self)
        self.triggersWidget.setAlternatingRowColors(True)
        self.layout().addWidget(self.triggersWidget)

        # Buttons
        self.dialogButtons = QDialogButtonBox(self)
        self.dialogButtons.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.layout().addWidget(self.dialogButtons)

        self.addButton = self.dialogButtons.addButton('Add', QDialogButtonBox.ActionRole)
        self.addButton.clicked.connect(self._add_trigger_dialog)

        self.delButton = self.dialogButtons.addButton('Remove', QDialogButtonBox.ActionRole)
        self.delButton.clicked.connect(self._remove_trigger)

        self.cue_dialog = CueListDialog(cues=Application().cue_model)

    def _add_new_trigger(self, tr_action, target, ta_action):
        item = QListWidgetItem()
        item.setSizeHint(QSize(200, 30))

        widget = TriggerWidget(tr_action, target, ta_action, self.cue_dialog)

        self.triggersWidget.addItem(item)
        self.triggersWidget.setItemWidget(item, widget)

    def _add_trigger_dialog(self):
        if self.cue_dialog.exec_() == QDialog.Accepted:
            target = self.cue_dialog.selected_cue()
            if target is not None:
                self._add_new_trigger(CueTriggers.Ended.value, target,
                                      CueAction.Start.value)

    def _remove_trigger(self):
        self.triggersWidget.takeItem(self.triggersWidget.currentRow())

    def load_settings(self, settings):
        # Remove the edited cue from the list of possible targets
        self_cue = Application().cue_model.get(settings.get('id'))
        if self_cue:
            self.cue_dialog.remove_cue(self_cue)

        settings = settings.get('triggers', {})

        for trigger_action, targets in settings.items():
            for target, target_action in targets:
                target = Application().cue_model.get(target)
                if target is not None:
                    self._add_new_trigger(trigger_action, target, target_action)

    def get_settings(self):
        triggers = {}

        for n in range(self.triggersWidget.count()):
            widget = self.triggersWidget.itemWidget(self.triggersWidget.item(n))
            tr_action, target, ta_action = widget.get_trigger()

            if tr_action not in triggers:
                triggers[tr_action] = []

            # Avoid duplicate
            if (target, ta_action) not in triggers[tr_action]:
                triggers[tr_action].append((target, ta_action))

        return {'triggers': triggers}


class TriggerWidget(QWidget):

    def __init__(self, tr_action, target, ta_action, cue_dialog, **kwargs):
        super().__init__(**kwargs)

        self.target = target
        self.cue_dialog = cue_dialog
        self.target_actions = {a.name: a.value for a in target.CueActions}

        self.setLayout(QHBoxLayout(self))
        self.layout().setContentsMargins(2, 1, 2, 1)

        self.triggerActions = QComboBox(self)
        # MediaTriggers members names and values are equals
        self.triggerActions.addItems([a.value for a in CueTriggers])
        self.triggerActions.setCurrentText(tr_action)
        self.layout().addWidget(self.triggerActions)

        self.selectButton = QPushButton(self)
        self.selectButton.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.selectButton.setText(target.name)
        self.selectButton.setToolTip(target.name)
        self.selectButton.clicked.connect(self.select_target)
        self.layout().addWidget(self.selectButton)

        self.targetActionCombo = QComboBox(self)
        self.targetActionCombo.addItems(self.target_actions.keys())
        self.targetActionCombo.setCurrentText(CueAction(ta_action).name)
        self.layout().addWidget(self.targetActionCombo)

        self.layout().setStretch(0, 1)
        self.layout().setStretch(1, 3)
        self.layout().setStretch(2, 1)

    def get_trigger(self):
        target = self.target.id
        tr_action = self.triggerActions.currentText()
        ta_action = self.target_actions[self.targetActionCombo.currentText()]

        return tr_action, target, ta_action

    def select_target(self):
        if self.cue_dialog.exec_() == QDialog.Accepted:
            target = self.cue_dialog.selected_cue()
            if target is not None:
                self.target = target
                self.selectButton.setText(self.target.name)
                self.selectButton.setToolTip(self.target.name)
