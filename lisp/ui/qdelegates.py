# This file is part of Linux Show Player
#
# Copyright 2019 Francesco Ceruti <ceppofrancy@gmail.com>
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

from enum import Enum

from PyQt5.QtCore import Qt, QEvent, QSize
from PyQt5.QtGui import QKeySequence, QFontMetrics
from PyQt5.QtWidgets import (
    QStyledItemDelegate,
    QComboBox,
    QSpinBox,
    QLineEdit,
    QStyle,
    QDialog,
    QCheckBox,
    QStyleOptionButton,
    qApp,
)

from lisp.cues.cue import CueAction
from lisp.ui.qmodels import CueClassRole
from lisp.ui.ui_utils import translate
from lisp.ui.widgets import CueActionComboBox, HotKeyEdit
from lisp.ui.widgets.cue_actions import tr_action
from lisp.ui.widgets.qenumcombobox import QEnumComboBox


class PaddedDelegate(QStyledItemDelegate):
    def __init__(self, hPad=0, vPad=0, **kwargs):
        super().__init__(**kwargs)
        self.hPad = hPad
        self.vPad = vPad

    def sizeHint(self, option, index):
        return super().sizeHint(option, index) + QSize(self.hPad, self.vPad)


class LabelDelegate(QStyledItemDelegate):
    def _text(self, option, index):
        return index.data()

    def paint(self, painter, option, index):
        self.initStyleOption(option, index)

        # Add 4px of left and right padding
        option.rect.adjust(4, 0, -4, 0)

        text = self._text(option, index)
        text = option.fontMetrics.elidedText(
            text, Qt.ElideRight, option.rect.width()
        )

        painter.save()

        if option.state & QStyle.State_Selected:
            painter.setBrush(option.palette.highlight())

            pen = painter.pen()
            pen.setBrush(option.palette.highlightedText())
            painter.setPen(pen)

        painter.drawText(option.rect, option.displayAlignment, text)

        painter.restore()

    def sizeHint(self, option, index):
        return QFontMetrics(option.font).size(
            Qt.TextSingleLine, self._text(option, index)
        ) + QSize(8, 0)


class ComboBoxDelegate(LabelDelegate):
    def __init__(self, options=(), tr_context=None, **kwargs):
        super().__init__(**kwargs)
        self.options = options
        self.tr_context = tr_context

    def _text(self, option, index):
        return translate(self.tr_context, index.data())

    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignCenter
        super().paint(painter, option, index)

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.setFrame(False)
        for option in self.options:
            editor.addItem(translate(self.tr_context, option), option)

        return editor

    def setEditorData(self, comboBox, index):
        value = index.model().data(index, Qt.EditRole)
        comboBox.setCurrentText(translate(self.tr_context, value))

    def setModelData(self, comboBox, model, index):
        model.setData(index, comboBox.currentData(), Qt.EditRole)

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


class BoolCheckBoxDelegate(QStyledItemDelegate):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def createEditor(self, parent, option, index):
        return None

    def _checkBoxRect(self, option):
        cbRect = option.rect
        cbSize = qApp.style().subElementRect(
            QStyle.SE_ViewItemCheckIndicator, QStyleOptionButton(), QCheckBox()
        )

        # Center the checkbox (horizontally)
        cbRect.moveLeft(
            option.rect.left() + (option.rect.width() - cbSize.width()) // 2
        )
        return cbRect

    def editorEvent(self, event, model, option, index):
        # If the "checkbox" is left-clicked change the current state
        if event.type() == QEvent.MouseButtonRelease:
            cbRect = self._checkBoxRect(option)
            if event.button() == Qt.LeftButton and cbRect.contains(event.pos()):
                value = bool(index.model().data(index, Qt.EditRole))
                model.setData(index, not value, Qt.EditRole)

                return True

        return super().editorEvent(event, model, option, index)

    def paint(self, painter, option, index):
        value = index.model().data(index, Qt.EditRole)
        cbOpt = QStyleOptionButton()

        cbOpt.state = QStyle.State_Enabled
        cbOpt.state |= QStyle.State_On if value else QStyle.State_Off
        cbOpt.rect = self._checkBoxRect(option)

        qApp.style().drawControl(
            QStyle.CE_CheckBox, cbOpt, painter, QCheckBox()
        )


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


class HotKeyEditDelegate(LabelDelegate):
    class Mode(Enum):
        KeySequence = 0
        NativeText = 1
        PortableText = 2

    def __init__(self, mode=Mode.PortableText, **kwargs):
        super().__init__(**kwargs)
        self.mode = mode

    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignHCenter | Qt.AlignVCenter
        super().paint(painter, option, index)

    def createEditor(self, parent, option, index):
        return HotKeyEdit(sequence=self._sequence(index), parent=parent)

    def setEditorData(self, editor: HotKeyEdit, index):
        editor.setKeySequence(self._sequence(index))

    def setModelData(self, editor: HotKeyEdit, model, index):
        sequence = editor.keySequence()
        if self.mode == HotKeyEditDelegate.Mode.NativeText:
            data = sequence.toString(QKeySequence.NativeText)
        elif self.mode == HotKeyEditDelegate.Mode.PortableText:
            data = sequence.toString(QKeySequence.PortableText)
        else:
            data = sequence

        model.setData(index, data, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def _text(self, option, index):
        return self._sequence(index).toString(QKeySequence.NativeText)

    def _sequence(self, index):
        data = index.data(Qt.EditRole)
        if self.mode == HotKeyEditDelegate.Mode.NativeText:
            return QKeySequence(data, QKeySequence.NativeText)
        elif self.mode == HotKeyEditDelegate.Mode.PortableText:
            return QKeySequence(data, QKeySequence.PortableText)

        return data


class EnumComboBoxDelegate(LabelDelegate):
    Mode = QEnumComboBox.Mode

    def __init__(self, enum, mode=Mode.Enum, trItem=str, **kwargs):
        super().__init__(**kwargs)
        self.enum = enum
        self.mode = mode
        self.trItem = trItem

    def _text(self, option, index):
        return self.trItem(self.itemFromData(index.data(Qt.EditRole)))

    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignHCenter | Qt.AlignVCenter
        super().paint(painter, option, index)

    def createEditor(self, parent, option, index):
        editor = QEnumComboBox(
            self.enum, mode=self.mode, trItem=self.trItem, parent=parent
        )
        editor.setFrame(False)

        return editor

    def setEditorData(self, editor, index):
        editor.setCurrentItem(index.data(Qt.EditRole))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentData(), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def itemFromData(self, data):
        if self.mode == EnumComboBoxDelegate.Mode.Name:
            return self.enum[data]
        elif self.mode == EnumComboBoxDelegate.Mode.Value:
            return self.enum(data)

        return data


class CueActionDelegate(EnumComboBoxDelegate):
    Mode = CueActionComboBox.Mode

    def __init__(self, cue_class=None, **kwargs):
        super().__init__(CueAction, trItem=tr_action, **kwargs)
        self.cue_class = cue_class

    def createEditor(self, parent, option, index):
        if self.cue_class is None:
            self.cue_class = index.data(CueClassRole)

        editor = CueActionComboBox(
            self.cue_class.CueActions, mode=self.mode, parent=parent
        )
        editor.setFrame(False)

        return editor


class CueSelectionDelegate(LabelDelegate):
    def __init__(self, cue_model, cue_select_dialog, **kwargs):
        super().__init__(**kwargs)
        self.cue_model = cue_model
        self.cue_select = cue_select_dialog

    def _text(self, option, index):
        cue = self.cue_model.get(index.data())
        if cue is not None:
            return f"{cue.index+1} | {cue.name}"

        return "UNDEF"

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseButtonDblClick:
            if self.cue_select.exec() == QDialog.Accepted:
                cue = self.cue_select.selected_cue()
                if cue is not None:
                    model.setData(index, cue.id, Qt.EditRole)
                    model.setData(index, cue.__class__, CueClassRole)
            return True

        return super().editorEvent(event, model, option, index)
