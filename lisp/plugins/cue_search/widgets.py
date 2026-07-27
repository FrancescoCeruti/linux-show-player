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

from PyQt5.QtGui import QAbstractTextDocumentLayout, QColor, QTextDocument
from PyQt5.QtWidgets import QStyle, QStyleOptionViewItem, QStyledItemDelegate, QTreeWidget
from PyQt5.QtCore import Qt

from lisp.ui.ui_utils import translate


class ResultList(QTreeWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.setRootIsDecorated(False)
        self.setUniformRowHeights(True)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QTreeWidget.SingleSelection)
        self.setEditTriggers(QTreeWidget.NoEditTriggers)
        self.setItemDelegateForColumn(1, HtmlDelagate(self))
        self.setItemDelegateForColumn(2, HtmlDelagate(self))
        self.setStyleSheet("""
            QWidget::item:selected,
            QWidget::item:selected:hover {
                color: palette(text);
                background-color: rgba(250, 220, 0, 100);
            }
        """)

        self.retranslateUi()

    def retranslateUi(self):
        self.setHeaderLabels((
            translate("CueSearch", "#"),
            translate("CueSearch", "Cue"),
            translate("CueSearch", "Description"),
        ))
        self.header().setStretchLastSection(True)


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
            palette.setColor(palette.All, palette.Highlight, QColor(250, 220, 0, 100))

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
            painter,
            QAbstractTextDocumentLayout.PaintContext()
        )

        painter.restore()
