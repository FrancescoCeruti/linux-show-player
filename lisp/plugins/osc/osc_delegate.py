# This file is part of Linux Show Player
#
# Copyright 2018 Francesco Ceruti <ceppofrancy@gmail.com>
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
from PyQt5.QtWidgets import (
    QStyledItemDelegate,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QLineEdit,
)

from lisp.plugins.osc.osc_server import OscMessageType


class OscArgumentDelegate(QStyledItemDelegate):
    MIN = -1_000_000
    MAX = 1_000_000
    DECIMALS = 4

    def __init__(self, tag=OscMessageType.Int, **kwargs):
        super().__init__(**kwargs)
        self.tag = tag

    def createEditor(self, parent, option, index):
        if self.tag is OscMessageType.Int:
            editor = QSpinBox(parent)
            editor.setRange(self.MIN, self.MAX)
            editor.setSingleStep(1)
        elif self.tag is OscMessageType.Float:
            editor = QDoubleSpinBox(parent)
            editor.setRange(self.MIN, self.MAX)
            editor.setDecimals(3)
            editor.setSingleStep(0.01)
        elif self.tag is OscMessageType.Bool:
            editor = QCheckBox(parent)
        elif self.tag is OscMessageType.String:
            editor = QLineEdit(parent)
            editor.setFrame(False)
        else:
            editor = None

        return editor

    def setEditorData(self, widget, index):
        value = index.model().data(index, Qt.EditRole)

        if self.tag is OscMessageType.Int:
            if isinstance(value, int):
                widget.setValue(value)
        elif self.tag is OscMessageType.Float:
            if isinstance(value, float):
                widget.setValue(value)
        elif self.tag is OscMessageType.Bool:
            if isinstance(value, bool):
                widget.setChecked(value)
        else:
            widget.setText(str(value))

    def setModelData(self, widget, model, index):
        if self.tag is OscMessageType.Int or self.tag is OscMessageType.Float:
            widget.interpretText()
            model.setData(index, widget.value(), Qt.EditRole)
        elif self.tag is OscMessageType.Bool:
            model.setData(index, widget.isChecked(), Qt.EditRole)
        else:
            model.setData(index, widget.text(), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def updateEditor(self, tag=None):
        if isinstance(tag, OscMessageType):
            self.tag = tag
        else:
            self.tag = None
