# This file is part of Linux Show Player
#
# Copyright 2026 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtCore import QEasingCurve, Qt, QVariantAnimation
from PyQt5.QtGui import (
    QAbstractTextDocumentLayout,
    QColor,
    QTextDocument,
)
from PyQt5.QtWidgets import (
    QStyle,
    QStyleOptionViewItem,
    QStyledItemDelegate,
    QTreeWidget,
)

from lisp.ui.ui_utils import translate


class ResultList(QTreeWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.setRootIsDecorated(False)
        self.setUniformRowHeights(True)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QTreeWidget.SingleSelection)
        self.setEditTriggers(QTreeWidget.NoEditTriggers)
        self.setItemDelegateForColumn(0, IconDelegate(self))
        self.setItemDelegateForColumn(2, HtmlDelagate(self))
        self.setItemDelegateForColumn(3, HtmlDelagate(self))
        self.header().setMinimumSectionSize(28)
        self.setStyleSheet(
            """
            QWidget::item:selected,
            QWidget::item:selected:hover {
                color: palette(text);
                background-color: rgba(250, 220, 0, 100);
            }
            """
        )

        self._fadePulse = QVariantAnimation(
            self,
            startValue=1.0,
            endValue=0.25,
            duration=1000,
            loopCount=-1,
            easingCurve=QEasingCurve.SineCurve,
        )
        self._fadePulse.valueChanged.connect(self._onFadePulse)

        self.retranslateUi()

    def setPulsing(self, pulsing):
        isRunning = self._fadePulse.state() == QVariantAnimation.Running

        if pulsing and not isRunning:
            self._fadePulse.start()
        elif not pulsing and isRunning:
            self._fadePulse.stop()

    def _onFadePulse(self, value):
        for row in range(self.topLevelItemCount()):
            item = self.topLevelItem(row)
            cue = item.data(0, Qt.UserRole)

            if cue.is_fading_out():
                self.update(self.indexFromItem(item, 0))

    def retranslateUi(self):
        self.setHeaderLabels(
            (
                "",
                translate("CueSearch", "#"),
                translate("CueSearch", "Cue"),
                translate("CueSearch", "Description"),
            )
        )
        self.header().setStretchLastSection(True)


class IconDelegate(QStyledItemDelegate):
    def __init__(self, view):
        super().__init__(view)
        self._view = view

    def sizeHint(self, option, index):
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        if options.decorationSize.isValid():
            return options.decorationSize

        return super().sizeHint(option, index)

    def paint(self, painter, option, index):
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        style = options.widget.style()
        iconRect = style.subElementRect(
            QStyle.SE_ItemViewItemDecoration, options, options.widget
        )

        # Draw the item without icon
        options.features &= ~QStyleOptionViewItem.HasDecoration
        style.drawControl(
            QStyle.CE_ItemViewItem, options, painter, options.widget
        )

        painter.save()

        # Use the pulse value for opacity, if fading
        cue = index.data(Qt.UserRole)
        if cue.is_fading_out():
            painter.setOpacity(self._view._fadePulse.currentValue())

        options.icon.paint(painter, iconRect)

        painter.restore()


class HtmlDelagate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setWidth(size.width() + 10)
        size.setHeight(size.height() + 8)

        return size

    def paint(self, painter, option, index):
        html = index.data(Qt.UserRole)

        if not html:
            return super().paint(painter, option, index)

        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        options.text = ""
        options.displayAlignment = Qt.AlignVCenter
        if options.state & QStyle.State_Selected:
            palette = options.palette
            palette.setColor(
                palette.All, palette.Highlight, QColor(250, 220, 0, 100)
            )

        # We use QTextDocument to render the text
        document = QTextDocument()
        document.setHtml(html)

        style = options.widget.style()

        docHeight = document.size().height()
        textRect = style.subElementRect(
            QStyle.SE_ItemViewItemText, options, options.widget
        )
        textRect.translate(0, -int(abs(docHeight - textRect.height()) / 2))

        painter.save()

        style.drawControl(QStyle.CE_ItemViewItem, options, painter)

        painter.translate(textRect.topLeft())

        document.documentLayout().draw(
            painter, QAbstractTextDocumentLayout.PaintContext()
        )

        painter.restore()
