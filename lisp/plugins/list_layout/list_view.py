# This file is part of Linux Show Player
#
# Copyright 2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtCore import (
    pyqtSignal,
    Qt,
    QDataStream,
    QIODevice,
    QT_TRANSLATE_NOOP,
)
from PyQt5.QtGui import QKeyEvent, QContextMenuEvent, QBrush, QColor
from PyQt5.QtWidgets import QTreeWidget, QHeaderView, QTreeWidgetItem

from lisp.core.signal import Connection
from lisp.cues.cue_factory import CueFactory
from lisp.plugins.list_layout.list_widgets import (
    CueStatusIcons,
    NameWidget,
    PreWaitWidget,
    CueTimeWidget,
    NextActionIcon,
    PostWaitWidget,
    IndexWidget,
)
from lisp.ui.ui_utils import translate


class ListColumn:
    def __init__(self, name, widget, resize=None, width=None, visible=True):
        self.baseName = name
        self.widget = widget
        self.resize = resize
        self.width = width
        self.visible = visible

    @property
    def name(self):
        return translate("ListLayoutHeader", self.baseName)


class CueTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, cue, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cue = cue
        self.current = False


# TODO: consider using a custom Model/View
class CueListView(QTreeWidget):
    keyPressed = pyqtSignal(QKeyEvent)
    contextMenuInvoked = pyqtSignal(QContextMenuEvent)

    # TODO: add ability to show/hide
    # TODO: implement columns (cue-type / target / etc..)
    COLUMNS = [
        ListColumn("", CueStatusIcons, QHeaderView.Fixed, width=45),
        ListColumn("#", IndexWidget, QHeaderView.ResizeToContents),
        ListColumn(
            QT_TRANSLATE_NOOP("ListLayoutHeader", "Cue"),
            NameWidget,
            QHeaderView.Stretch,
        ),
        ListColumn(
            QT_TRANSLATE_NOOP("ListLayoutHeader", "Pre wait"), PreWaitWidget
        ),
        ListColumn(
            QT_TRANSLATE_NOOP("ListLayoutHeader", "Action"), CueTimeWidget
        ),
        ListColumn(
            QT_TRANSLATE_NOOP("ListLayoutHeader", "Post wait"), PostWaitWidget
        ),
        ListColumn("", NextActionIcon, QHeaderView.Fixed, width=18),
    ]

    ITEM_DEFAULT_BG = QBrush(Qt.transparent)
    ITEM_CURRENT_BG = QBrush(QColor(250, 220, 0, 100))

    def __init__(self, listModel, parent=None):
        """
        :type listModel: lisp.plugins.list_layout.models.CueListModel
        """
        super().__init__(parent)

        self.__itemMoving = False
        self.__scrollRangeGuard = False

        # Watch for model changes
        self._model = listModel
        self._model.item_added.connect(self.__cueAdded, Connection.QtQueued)
        self._model.item_moved.connect(self.__cueMoved, Connection.QtQueued)
        self._model.item_removed.connect(self.__cueRemoved, Connection.QtQueued)
        self._model.model_reset.connect(self.__modelReset)

        # Setup the columns headers
        self.setHeaderLabels((c.name for c in CueListView.COLUMNS))
        for i, column in enumerate(CueListView.COLUMNS):
            if column.resize is not None:
                self.header().setSectionResizeMode(i, column.resize)
            if column.width is not None:
                self.setColumnWidth(i, column.width)

        self.header().setDragEnabled(False)
        self.header().setStretchLastSection(False)

        self.setDragDropMode(self.InternalMove)

        # Set some visual options
        self.setIndentation(0)
        self.setAlternatingRowColors(True)
        self.setVerticalScrollMode(self.ScrollPerItem)

        # This allow to have some spared space at the end of the scroll-area
        self.verticalScrollBar().rangeChanged.connect(self.__updateScrollRange)
        self.currentItemChanged.connect(self.__currentItemChanged)

    def dropEvent(self, event):
        # Decode mimedata information about the drag&drop event, since only
        # internal movement are allowed we assume the data format is correct
        data = event.mimeData().data("application/x-qabstractitemmodeldatalist")
        stream = QDataStream(data, QIODevice.ReadOnly)

        # Get the starting-item row
        to_index = self.indexAt(event.pos()).row()
        if not 0 <= to_index <= len(self._model):
            to_index = len(self._model)

        rows = []
        while not stream.atEnd():
            row = stream.readInt()
            # Skip column and data
            stream.readInt()
            for _ in range(stream.readInt()):
                stream.readInt()
                stream.readQVariant()

            if rows and row == rows[-1]:
                continue

            rows.append(row)

        if event.proposedAction() == Qt.MoveAction:
            before = 0
            after = 0
            for row in sorted(rows):
                if row < to_index:
                    self._model.move(row - before, to_index)
                    before += 1
                elif row > to_index:
                    # if we have already moved something we need to shift,
                    # bool(before) is evaluated as 1 (True) or 0 (False)
                    self._model.move(row, to_index + after + bool(before))
                    after += 1
        elif event.proposedAction() == Qt.CopyAction:
            # TODO: add a copy/clone method to the model?
            new_cues = []
            for row in sorted(rows):
                new_cues.append(CueFactory.clone_cue(self._model.item(row)))

            for cue in new_cues:
                self._model.insert(cue, to_index)
                to_index += 1

    def contextMenuEvent(self, event):
        self.contextMenuInvoked.emit(event)

    def keyPressEvent(self, event):
        event.ignore()
        self.keyPressed.emit(event)
        # If the event object has been accepted during the `keyPressed`
        # emission don't call the base implementation
        if not event.isAccepted():
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if (
            not event.buttons() & Qt.RightButton
            or not self.selectionMode() == QTreeWidget.NoSelection
        ):
            super().mousePressEvent(event)

    def standbyIndex(self):
        return self.indexOfTopLevelItem(self.currentItem())

    def setStandbyIndex(self, newIndex):
        if 0 <= newIndex < self.topLevelItemCount():
            self.setCurrentItem(self.topLevelItem(newIndex))

    def __currentItemChanged(self, current, previous):
        if previous is not None:
            self.__updateItem(previous, False)

        if current is not None:
            self.__updateItem(current, True)
            if self.selectionMode() == QTreeWidget.NoSelection:
                # ensure the current item is in the middle
                self.scrollToItem(current, QTreeWidget.PositionAtCenter)

    def __updateItem(self, item, current):
        item.current = current
        if current:
            background = CueListView.ITEM_CURRENT_BG
        else:
            background = CueListView.ITEM_DEFAULT_BG

        for column in range(self.columnCount()):
            item.setBackground(column, background)

    def __cueAdded(self, cue):
        item = CueTreeWidgetItem(cue)
        item.setFlags(item.flags() & ~Qt.ItemIsDropEnabled)

        self.insertTopLevelItem(cue.index, item)
        self.__setupItemWidgets(item)

        if self.topLevelItemCount() == 1:
            # If it's the only item in the view, set it as current
            self.setCurrentItem(item)
        else:
            # Scroll to the last item added
            self.scrollToItem(item)

        # Ensure that the focus is set
        self.setFocus()

    def __cueMoved(self, before, after):
        item = self.takeTopLevelItem(before)
        self.insertTopLevelItem(after, item)
        self.__setupItemWidgets(item)

    def __cueRemoved(self, cue):
        index = cue.index
        self.takeTopLevelItem(index)

    def __modelReset(self):
        self.reset()
        self.clear()

    def __setupItemWidgets(self, item):
        for i, column in enumerate(CueListView.COLUMNS):
            self.setItemWidget(item, i, column.widget(item))

        self.updateGeometries()

    def __updateScrollRange(self, min_, max_):
        if not self.__scrollRangeGuard:
            self.__scrollRangeGuard = True
            self.verticalScrollBar().setMaximum(max_ + 1)
            self.__scrollRangeGuard = False
