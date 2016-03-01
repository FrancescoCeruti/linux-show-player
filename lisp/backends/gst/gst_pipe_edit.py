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
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QGridLayout, QComboBox, QListWidget, \
    QAbstractItemView, QVBoxLayout, QPushButton, QDialogButtonBox, QWidget

from lisp.backends.gst import elements


class GstPipeEdit(QWidget):

    def __init__(self, pipe, app_mode=False, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QGridLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self._app_mode = app_mode

        # Input selection
        self.inputBox = QComboBox(self)
        self.layout().addWidget(self.inputBox, 0, 0, 1, 3)
        self.__init_inputs()

        # Current plugins list
        self.currentList = QListWidget(self)
        self.currentList.setDragEnabled(True)
        self.currentList.setDragDropMode(QAbstractItemView.InternalMove)
        self.layout().addWidget(self.currentList, 1, 0)

        # Available plugins list
        self.availableList = QListWidget(self)
        self.layout().addWidget(self.availableList, 1, 2)

        # Output selection
        self.outputBox = QComboBox(self)
        self.layout().addWidget(self.outputBox, 4, 0, 1, 3)
        self.__init_outputs()

        # Add/Remove plugins buttons
        self.buttonsLayout = QVBoxLayout()
        self.layout().addLayout(self.buttonsLayout, 1, 1)
        self.layout().setAlignment(self.buttonsLayout, Qt.AlignHCenter)

        self.addButton = QPushButton(self)
        self.addButton.setIcon(QIcon.fromTheme('go-previous'))
        self.addButton.clicked.connect(self.__add_plugin)
        self.buttonsLayout.addWidget(self.addButton)
        self.buttonsLayout.setAlignment(self.addButton, Qt.AlignHCenter)

        self.delButton = QPushButton(self)
        self.delButton.setIcon(QIcon.fromTheme('go-next'))
        self.delButton.clicked.connect(self.__remove_plugin)
        self.buttonsLayout.addWidget(self.delButton)
        self.buttonsLayout.setAlignment(self.delButton, Qt.AlignHCenter)

        # Load the pipeline
        self.set_pipe(pipe)

    def set_pipe(self, pipe):
        if pipe:
            if not self._app_mode:
                inputs = sorted(elements.inputs())
                self.inputBox.setCurrentIndex(inputs.index(pipe[0]))

            outputs = sorted(elements.outputs())
            self.outputBox.setCurrentIndex(outputs.index(pipe[-1]))

        self.__init_current_plugins(pipe)
        self.__init_available_plugins(pipe)

    def get_pipe(self):
        pipe = [] if self._app_mode else [self.inputBox.currentText()]
        for n in range(self.currentList.count()):
            pipe.append(self.currentList.item(n).text())
        pipe.append(self.outputBox.currentText())

        return tuple(pipe)

    def __init_inputs(self):
        if self._app_mode:
            self.inputBox.setEnabled(False)
        else:
            inputs = sorted(elements.inputs())
            self.inputBox.addItems(inputs)
            self.inputBox.setEnabled(len(inputs) > 1)

    def __init_outputs(self):
        outputs = sorted(elements.outputs())
        self.outputBox.addItems(outputs)
        self.outputBox.setEnabled(len(outputs) > 1)

    def __init_current_plugins(self, pipe):
        self.currentList.clear()

        start = 0 if self._app_mode else 1
        for plugin in pipe[start:-1]:
            self.currentList.addItem(plugin)

    def __init_available_plugins(self, pipe):
        self.availableList.clear()

        for plugin in elements.plugins().values():
            if plugin.Name not in pipe:
                self.availableList.addItem(plugin.Name)

    def __add_plugin(self):
        item = self.availableList.takeItem(self.availableList.currentRow())
        self.currentList.addItem(item)

    def __remove_plugin(self):
        item = self.currentList.takeItem(self.currentList.currentRow())
        self.availableList.addItem(item)


class GstPipeEditDialog(QDialog):

    def __init__(self, pipe, app_mode=False, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.setWindowTitle('Edit Pipeline')
        self.setWindowModality(Qt.ApplicationModal)
        self.setMaximumSize(500, 400)
        self.setMinimumSize(500, 400)
        self.resize(500, 400)

        # GstPipeEdit
        self.pipeEdit = GstPipeEdit(pipe, app_mode=app_mode, parent=self)
        self.layout().addWidget(self.pipeEdit)

        # Confirm/Cancel buttons
        self.dialogButtons = QDialogButtonBox(self)
        self.dialogButtons.setStandardButtons(QDialogButtonBox.Cancel |
                                              QDialogButtonBox.Ok)
        self.layout().addWidget(self.dialogButtons)

        self.dialogButtons.accepted.connect(self.accept)
        self.dialogButtons.rejected.connect(self.reject)

    def get_pipe(self):
        return self.pipeEdit.get_pipe()