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
from PyQt5.QtWidgets import QStyledItemDelegate, QComboBox, QSpinBox, QLineEdit


class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, options=(), **kwargs):
        super().__init__(**kwargs)
        self.options = options

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.setFrame(False)
        editor.addItems(self.options)

        return editor

    def setEditorData(self, comboBox, index):
        value = index.model().data(index, Qt.EditRole)
        comboBox.setCurrentText(value)

    def setModelData(self, comboBox, model, index):
        model.setData(index, comboBox.currentText(), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class SpinBoxDelegate(QStyledItemDelegate):
    def __init__(self, minimum=-100, maximum=100, step=1, **kwargs):
        super().__init__(**kwargs)

        self.minimum = minimum
        self.maximum = maximum
        self.step = step

    def createEditor(self, parent, option, index):
        editor = QSpinBox(parent)
        editor.setRange(self.minimum, self.maximum)
        editor.setSingleStep(self.step)

        return editor

    def setEditorData(self, spinBox, index):
        value = index.model().data(index, Qt.EditRole)
        if isinstance(value, int):
            spinBox.setValue(value)

    def setModelData(self, spinBox, model, index):
        spinBox.interpretText()
        model.setData(index, spinBox.value(), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class LineEditDelegate(QStyledItemDelegate):

    def __init__(self, max_length=-1, validator=None, **kwargs):
        super().__init__(**kwargs)

        self.max_length = max_length
        self.validator = validator

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        if self.max_length > 0:
            editor.setMaxLength(self.max_length)
        if self.validator is not None:
            editor.setValidator(self.validator)
        editor.setFrame(False)

        return editor

    def setEditorData(self, lineEdit, index):
        value = index.model().data(index, Qt.EditRole)
        lineEdit.setText(str(value))

    def setModelData(self, lineEdit, model, index):
        model.setData(index, lineEdit.text(), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
