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

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QGridLayout, QComboBox, QListWidget, \
    QAbstractItemView, QVBoxLayout, QPushButton, QDialogButtonBox

from lisp.backends.gst import elements


class GstPipeEdit(QDialog):

    def __init__(self, pipe, preferences_mode=False, **kwargs):
        super().__init__(**kwargs)

        self.setWindowTitle('Edit Pipeline')
        self.setWindowModality(Qt.ApplicationModal)
        self.setLayout(QGridLayout())
        self.setMaximumSize(500, 400)
        self.setMinimumSize(500, 400)
        self.resize(500, 400)

        self._preferences_mode = preferences_mode

        # Input selection
        self.inputBox = QComboBox(self)
        self.layout().addWidget(self.inputBox, 0, 0, 1, 3)
        self.init_inputs(pipe)

        # Current plugins list
        self.currentList = QListWidget(self)
        self.currentList.setDragEnabled(True)
        self.currentList.setDragDropMode(QAbstractItemView.InternalMove)
        self.layout().addWidget(self.currentList, 1, 0, 3, 1)
        self.init_current_plugins(pipe)

        # Add/Remove plugins buttons
        self.pluginsLayout = QVBoxLayout()
        self.layout().addLayout(self.pluginsLayout, 2, 1)

        self.addButton = QPushButton(self)
        self.addButton.setIcon(QIcon.fromTheme('go-previous'))
        self.addButton.clicked.connect(self.__add_plugin)
        self.pluginsLayout.addWidget(self.addButton)
        self.pluginsLayout.setAlignment(self.addButton, Qt.AlignHCenter)

        self.delButton = QPushButton(self)
        self.delButton.setIcon(QIcon.fromTheme('go-next'))
        self.delButton.clicked.connect(self.__remove_plugin)
        self.pluginsLayout.addWidget(self.delButton)
        self.pluginsLayout.setAlignment(self.delButton, Qt.AlignHCenter)

        # Available plugins list
        self.availableList = QListWidget(self)
        self.layout().addWidget(self.availableList, 1, 2, 3, 1)
        self.init_available_plugins(pipe)

        # Output selection
        self.outputBox = QComboBox(self)
        self.layout().addWidget(self.outputBox, 4, 0, 1, 3)
        self.init_outputs(pipe)

        # Confirm/Cancel buttons
        self.dialogButtons = QDialogButtonBox(self)
        self.dialogButtons.setStandardButtons(QDialogButtonBox.Cancel |
                                              QDialogButtonBox.Ok)
        self.layout().addWidget(self.dialogButtons, 5, 0, 1, 3)

        self.dialogButtons.accepted.connect(self.accept)
        self.dialogButtons.rejected.connect(self.reject)

    def init_inputs(self, pipe):
        if self._preferences_mode:
            self.inputBox.setEnabled(False)
        else:
            inputs = sorted(elements.inputs())
            self.inputBox.addItems(inputs)
            self.inputBox.setEnabled(len(inputs) > 1)
            if len(pipe) > 0:
                self.inputBox.setCurrentIndex(inputs.index(pipe[0]))

    def init_outputs(self, pipe):
        outputs = sorted(elements.outputs())
        self.outputBox.addItems(outputs)
        self.outputBox.setEnabled(len(outputs) > 1)
        if len(pipe) > 0:
            self.outputBox.setCurrentIndex(outputs.index(pipe[-1]))

    def init_current_plugins(self, pipe):
        start = 0 if self._preferences_mode else 1
        for plugin in pipe[start:-1]:
            self.currentList.addItem(plugin)

    def init_available_plugins(self, pipe):
        for plugin in elements.plugins().values():
            if plugin.Name not in pipe:
                self.availableList.addItem(plugin.Name)

    def get_pipe(self):
        pipe = [] if self._preferences_mode else [self.inputBox.currentText()]
        for n in range(self.currentList.count()):
            pipe.append(self.currentList.item(n).text())
        pipe.append(self.outputBox.currentText())

        return tuple(pipe)

    def __add_plugin(self):
        item = self.availableList.takeItem(self.availableList.currentRow())
        self.currentList.addItem(item)

    def __remove_plugin(self):
        item = self.currentList.takeItem(self.currentList.currentRow())
        self.availableList.addItem(item)
