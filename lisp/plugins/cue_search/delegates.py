from PyQt5.QtGui import QAbstractTextDocumentLayout, QColor, QTextDocument
from PyQt5.QtWidgets import QStyle, QStyleOptionViewItem, QStyledItemDelegate
from PyQt5.QtCore import Qt


class CueSearchHighlightDelegate(QStyledItemDelegate):

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
