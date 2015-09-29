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
from PyQt5.QtWidgets import QVBoxLayout, QListWidget, QDialogButtonBox, \
    QSizePolicy, QListWidgetItem, QDialog, QWidget, QHBoxLayout, QComboBox, \
    QPushButton

from lisp.application import Application
from lisp.plugins.triggers.triggers_handler import MediaTriggers
from lisp.ui.cuelistdialog import CueListDialog
from lisp.ui.settings.section import SettingsSection


class TriggersSettings(SettingsSection):

    Name = 'Triggers'
    PluginInstance = None

    def __init__(self, size, cue=None, **kwargs):
        super().__init__(size, cue=None, **kwargs)
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

        self.cue = cue

        if self.cue is None:
            self.setEnabled(False)
        else:
            self.cue_dialog = CueListDialog()
            self.cue_dialog.add_cues(Application().layout.get_cues())

    def _add_new_trigger(self, tr_action, target, ta_action):
        item = QListWidgetItem()
        item.setSizeHint(QSize(200, 30))

        widget = TriggerWidget(self.cue, tr_action, target, ta_action,
                               self.cue_dialog)

        self.triggersWidget.addItem(item)
        self.triggersWidget.setItemWidget(item, widget)

    def _add_trigger_dialog(self):
        if self.cue_dialog.exec_() == QDialog.Accepted:
            target = self.cue_dialog.selected_cues()[0]
            self._add_new_trigger(tuple(MediaTriggers)[0].value, target,
                                  tuple(target.CueAction)[0].value)

    def _remove_trigger(self):
        self.triggersWidget.takeItem(self.triggersWidget.currentRow())

    def set_configuration(self, conf):
        if self.PluginInstance is not None and self.cue is not None:
            triggers = self.PluginInstance.triggers.get(self.cue.id, {})

            for trigger_action, targets in triggers.items():
                for target, target_action in targets:
                    target = Application().layout.get_cue_by_id(target)
                    if target is not None:
                        self._add_new_trigger(trigger_action, target, target_action)

    def get_configuration(self):
        if self.PluginInstance is not None and self.cue is not None:
            triggers = {}

            for n in range(self.triggersWidget.count()):
                trigger = self.triggersWidget.itemWidget(self.triggersWidget.item(n))
                tr_action, target, ta_action = trigger.get_trigger()

                if tr_action in triggers:
                    triggers[tr_action].append((target, ta_action))
                else:
                    triggers[tr_action] = [(target, ta_action)]

            self.PluginInstance.update_handler(self.cue, triggers)

        return {}


class TriggerWidget(QWidget):

    def __init__(self, cue, tr_action, target, ta_action, cue_dialog,
                 time_mode=False, **kwargs):
        super().__init__(**kwargs)

        self.cue = cue
        self.target = target
        self.cue_dialog = cue_dialog
        self.target_actions = {m.name: m.value for m in target.CueAction}
        self._time_mode = time_mode

        self.setLayout(QHBoxLayout(self))
        self.layout().setContentsMargins(2, 1, 2, 1)

        self.triggerActions = QComboBox(self)
        # MediaTriggers members names and values are equals
        self.triggerActions.addItems([m.value for m in MediaTriggers])
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
        self.targetActionCombo.setCurrentText(target.CueAction(ta_action).name)
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
            self.target = self.cue_dialog.selected_cues()[0]
            self.selectButton.setText(self.target.name)
