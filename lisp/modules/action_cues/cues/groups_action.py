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


from PyQt5 import QtCore
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QHBoxLayout, QLineEdit, \
    QSizePolicy, QLabel, QComboBox

from lisp.application import Application
from lisp.core.decorators import async
from lisp.cues.cue import Cue
from lisp.cues.media_cue import MediaCue
from lisp.layouts.cue_layout import CueLayout
from lisp.ui.settings.section import SettingsSection


class GroupsAction(Cue):

    _properties_ = ['groups', 'action']
    _properties_.extend(Cue._properties_)

    Name = 'Groups action'
    Actions = {action.name: action for action in MediaCue.CueAction}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.groups = []
        if 'Default' in GroupsAction.Actions:
            self.action = 'Default'
        else:
            self.action = GroupsAction.Actions.keys()[0]

    @async
    def execute(self, action=Cue.CueAction.Default):
        self.on_execute.emit(self, action)

        cue_action = GroupsAction.Actions.get(self.action,
                                              MediaCue.CueAction.Default)
        layout = Application().layout
        for cue in layout.get_cues(cue_class=MediaCue):
            if not set(cue['groups']).isdisjoint(self.groups):
                cue.execute(action=cue_action)

        self.executed.emit(self, action)


class GroupsActionSettings(SettingsSection):

    Name = 'Cue Settings'
    Actions = [action.name for action in MediaCue.CueAction].sort()

    def __init__(self, size, cue=None, parent=None):
        super().__init__(size, cue=cue, parent=parent)

        self.setLayout(QVBoxLayout(self))

        # Groups
        self.groupGroups = QGroupBox(self)
        self.groupGroups.setTitle("Edit groups")
        self.ggHLayout = QHBoxLayout(self.groupGroups)

        self.editGroups = QLineEdit(self.groupGroups)
        regex = QtCore.QRegExp('(\d+,)*')
        self.editGroups.setValidator(QRegExpValidator(regex))
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.editGroups.setSizePolicy(sizePolicy)
        self.ggHLayout.addWidget(self.editGroups)

        self.groupsEditLabel = QLabel(self.groupGroups)
        self.groupsEditLabel.setText("Modify groups [0,1,2,...,n]")
        self.groupsEditLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.ggHLayout.addWidget(self.groupsEditLabel)

        self.layout().addWidget(self.groupGroups)

        # Action
        self.groupAction = QGroupBox(self)
        self.groupAction.setTitle("Select action")
        self.gaHLayout = QHBoxLayout(self.groupAction)

        self.actionsBox = QComboBox(self.groupAction)
        self.actionsBox.addItems(self.Actions)
        self.gaHLayout.addWidget(self.actionsBox)

        self.layout().addWidget(self.groupAction)
        self.layout().addSpacing(self.height() - 200)

    def get_configuration(self):
        conf = {}

        checkable = self.groupGroups.isCheckable()

        if not (checkable and not self.groupGroups.isChecked()):
            groups_str = self.editGroups.text().split(',')
            if groups_str[-1] != '':
                conf['groups'] = [int(groups_str[-1])]
            else:
                conf['groups'] = []
            conf['groups'] += [int(g) for g in groups_str[:-1]]
        if not (checkable and not self.groupAction.isChecked()):
            conf['action'] = self.actionsBox.currentText().lower()

        return conf

    def enable_check(self, enable):
        self.groupGroups.setCheckable(enable)
        self.groupGroups.setChecked(False)

        self.groupAction.setCheckable(enable)
        self.groupAction.setChecked(False)

    def set_configuration(self, conf):
        if 'groups' in conf:
            self.editGroups.setText(str(conf['groups'])[1:-1])
        if 'action' in conf and conf['action'] in self.Actions:
            index = self.Actions.index(conf['action'].title())
            self.actionsBox.setCurrentIndex(index)


CueLayout.add_settings_section(GroupsActionSettings, GroupsAction)
