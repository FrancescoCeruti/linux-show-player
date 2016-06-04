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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QGridLayout, QTableView, QHeaderView, \
    QTableWidget, QPushButton, QVBoxLayout

from lisp.application import Application
from lisp.plugins.controller.protocols.protocol import Protocol
from lisp.ui.qdelegates import ComboBoxDelegate, LineEditDelegate
from lisp.ui.qmodels import SimpleTableModel
from lisp.ui.settings.settings_page import CueSettingsPage


class Keyboard(Protocol):

    def init(self):
        Application().layout.key_pressed.connect(self.__key_pressed)

    def reset(self):
        Application().layout.key_pressed.disconnect(self.__key_pressed)

    def __key_pressed(self, key_event):
        if not key_event.isAutoRepeat() and key_event.text() != '':
            self.protocol_event.emit(key_event.text())


class KeyboardSettings(CueSettingsPage):
    Name = 'Keyboard shortcuts'

    def __init__(self, cue_class, **kwargs):
        super().__init__(cue_class, **kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.keyGroup = QGroupBox(self)
        self.keyGroup.setTitle('Hot-Keys')
        self.keyGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.keyGroup)

        self.keyboardModel = SimpleTableModel(['Key', 'Action'])

        self.keyboardView = KeyboardView(cue_class, parent=self.keyGroup)
        self.keyboardView.setModel(self.keyboardModel)
        self.keyGroup.layout().addWidget(self.keyboardView, 0, 0, 1, 2)

        self.addButton = QPushButton('Add', self.keyGroup)
        self.addButton.clicked.connect(self.__new_key)
        self.keyGroup.layout().addWidget(self.addButton, 1, 0)

        self.removeButton = QPushButton('Remove', self.keyGroup)
        self.removeButton.clicked.connect(self.__remove_key)
        self.keyGroup.layout().addWidget(self.removeButton, 1, 1)

    def enable_check(self, enabled):
        self.keyGroup.setCheckable(enabled)
        self.keyGroup.setChecked(False)

    def get_settings(self):
        settings = {}

        if not (self.keyGroup.isCheckable() and not self.keyGroup.isChecked()):
            settings['keyboard'] = self.keyboardModel.rows

        return settings

    def load_settings(self, settings):
        for key, action in settings.get('keyboard', []):
            self.keyboardModel.appendRow(key, action)

    def __new_key(self):
        self.keyboardModel.appendRow('', self._cue_class.CueActions[0].name)

    def __remove_key(self):
        self.keyboardModel.removeRow(self.keyboardView.currentIndex().row())


class KeyboardView(QTableView):

    def __init__(self, cue_class, **kwargs):
        super().__init__(**kwargs)

        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)

        self.setShowGrid(False)
        self.setAlternatingRowColors(True)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setHighlightSections(False)

        self.verticalHeader().sectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(24)
        self.verticalHeader().setHighlightSections(False)

        cue_actions = [action.name for action in cue_class.CueActions]
        self.delegates = [LineEditDelegate(max_length=1),
                          ComboBoxDelegate(options=cue_actions)]

        for column, delegate in enumerate(self.delegates):
            self.setItemDelegateForColumn(column, delegate)
