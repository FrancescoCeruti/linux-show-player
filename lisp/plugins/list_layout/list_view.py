# This file is part of Linux Show Player
#
# Copyright 2022 Francesco Ceruti <ceppofrancy@gmail.com>
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

from dataclasses import dataclass
from functools import partial
from typing import Type

from PyQt5.QtCore import (
    QT_TRANSLATE_NOOP,
    QDataStream,
    QIODevice,
    Qt,
    pyqtSignal,
)
from PyQt5.QtGui import QBrush, QColor, QContextMenuEvent, QKeyEvent
from PyQt5.QtWidgets import (
    QHeaderView,
    QMenu,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)

from lisp.application import Application
from lisp.backend import get_backend
from lisp.command.model import ModelInsertItemsCommand, ModelMoveItemsCommand
from lisp.core.util import subdict
from lisp.plugins.list_layout.list_widgets import (
    CueStatusIcons,
    CueTimeWidget,
    IndexWidget,
    NameWidget,
    NextActionIcon,
    PostWaitWidget,
    PreWaitWidget,
)
from lisp.ui.ui_utils import css_to_dict, dict_to_css, translate


@dataclass
class ListColumn:
    id: str
    baseName: str
    widget: Type[QWidget]
    resize: QHeaderView.ResizeMode | None = None
    width: int | None = None
    canHide: bool = True
    hideName: bool = False

    def headerText(self):
        if self.hideName:
            return ""

        return self.name

    @property
    def name(self):
        return translate("ListLayoutHeader", self.baseName)


class CueTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, cue, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cue = cue
        self.current = False


# TODO: use a custom Model/View
class CueListView(QTreeWidget):
    keyPressed = pyqtSignal(QKeyEvent)
    contextMenuInvoked = pyqtSignal(QContextMenuEvent)

    COLUMNS = [
        ListColumn(
            "status",
            QT_TRANSLATE_NOOP("ListLayoutHeader", "Cue Status"),
            CueStatusIcons,
            resize=QHeaderView.Fixed,
            width=45,
            hideName=True,
            canHide=False,
        ),
        ListColumn(
            "cue_index",
            "#",
            IndexWidget,
            resize=QHeaderView.ResizeToContents,
        ),
        ListColumn(
            "name",
            QT_TRANSLATE_NOOP("ListLayoutHeader", "Cue"),
            NameWidget,
            resize=QHeaderView.Stretch,
            canHide=False,
        ),
        ListColumn(
            "pre_wait_time",
            QT_TRANSLATE_NOOP("ListLayoutHeader", "Pre wait"),
            PreWaitWidget,
        ),
        ListColumn(
            "action_time",
            QT_TRANSLATE_NOOP("ListLayoutHeader", "Action"),
            CueTimeWidget,
            canHide=False,
        ),
        ListColumn(
            "post_wait_time",
            QT_TRANSLATE_NOOP("ListLayoutHeader", "Post wait"),
            PostWaitWidget,
        ),
        ListColumn(
            "next_action",
            QT_TRANSLATE_NOOP("ListLayoutHeader", "Next Action"),
            NextActionIcon,
            resize=QHeaderView.Fixed,
            width=18,
            hideName=True,
        ),
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
        self._model.item_added.connect(self.__cueAdded)
        self._model.item_moved.connect(self.__cueMoved)
        self._model.item_removed.connect(self.__cueRemoved)
        self._model.model_reset.connect(self.__modelReset)

        # Create context menu for column headers
        self.columnMenu = QMenu()

        # Columns headers setup
        self.setColumnCount(len(CueListView.COLUMNS))

        for i, column in enumerate(CueListView.COLUMNS):
            self.headerItem().setText(i, column.headerText())

            if column.resize is not None:
                self.header().setSectionResizeMode(i, column.resize)
            if column.width is not None:
                self.setColumnWidth(i, column.width)

        self.header().setDragEnabled(True)
        self.header().setStretchLastSection(False)
        self.header().setContextMenuPolicy(Qt.CustomContextMenu)
        self.header().customContextMenuRequested.connect(self.__openHeaderMenu)

        self.setDragDropMode(self.InternalMove)

        # Set some visual options
        self.setIndentation(0)
        self.setAlternatingRowColors(True)
        self.setVerticalScrollMode(self.ScrollPerItem)

        # This allows to have some spare space at the end of the scroll-area
        self.verticalScrollBar().rangeChanged.connect(self.__updateScrollRange)
        self.currentItemChanged.connect(
            self.__currentItemChanged, Qt.QueuedConnection
        )

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            if all([x.isLocalFile() for x in event.mimeData().urls()]):
                event.accept()
            else:
                event.ignore()
        else:
            return super().dragEnterEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            # If files are being dropped, add them as cues
            get_backend().add_cue_from_urls(event.mimeData().urls())
        else:
            # Otherwise copy/move existing cue.

            # Decode mimedata information about the drag&drop event, since only
            # internal movement are allowed we assume the data format is correct
            data = event.mimeData().data(
                "application/x-qabstractitemmodeldatalist"
            )
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
                Application().commands_stack.do(
                    ModelMoveItemsCommand(self._model, rows, to_index)
                )
            elif event.proposedAction() == Qt.CopyAction:
                new_cues = []
                for row in sorted(rows):
                    new_cues.append(
                        Application().cue_factory.clone_cue(
                            self._model.item(row)
                        )
                    )

                Application().commands_stack.do(
                    ModelInsertItemsCommand(self._model, to_index, *new_cues)
                )

    def contextMenuEvent(self, event):
        self.contextMenuInvoked.emit(event)

    def keyPressEvent(self, event):
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
            previous.current = False
            self.__updateItemStyle(previous)

        if current is not None:
            current.current = True
            self.__updateItemStyle(current)

            if self.selectionMode() == QTreeWidget.NoSelection:
                # Ensure the current item is in the middle of the viewport.
                # This is skipped in "selection-mode" otherwise it creates
                # confusion during drag&drop operations
                self.scrollToItem(current, QTreeWidget.PositionAtCenter)
            elif not self.selectedIndexes():
                current.setSelected(True)

    def __updateItemStyle(self, item):
        if item.treeWidget() is not None:
            css = css_to_dict(item.cue.stylesheet)
            brush = QBrush()

            if item.current:
                widget_css = subdict(css, ("font-size",))
                brush = CueListView.ITEM_CURRENT_BG
            else:
                widget_css = subdict(css, ("color", "font-size"))
                css_bg = css.get("background")
                if css_bg is not None:
                    color = QColor(css_bg)
                    color.setAlpha(150)
                    brush = QBrush(color)

            for column in range(self.columnCount()):
                self.itemWidget(item, column).setStyleSheet(
                    dict_to_css(widget_css)
                )
                item.setBackground(column, brush)

    def __cuePropChanged(self, cue, property_name, _):
        if property_name == "stylesheet":
            self.__updateItemStyle(self.topLevelItem(cue.index))

    def __cueAdded(self, cue):
        item = CueTreeWidgetItem(cue)
        item.setFlags(item.flags() & ~Qt.ItemIsDropEnabled)
        cue.property_changed.connect(self.__cuePropChanged)

        self.insertTopLevelItem(cue.index, item)
        self.__setupItemWidgets(item)
        self.__updateItemStyle(item)

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
        cue.property_changed.disconnect(self.__cuePropChanged)
        self.takeTopLevelItem(cue.index)

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

    def __toggleColumn(self, checked, index):
        if checked:
            self.showColumn(index)
        else:
            self.hideColumn(index)

    def __openHeaderMenu(self, position):
        for index, column in enumerate(CueListView.COLUMNS):
            if column.canHide:
                toggleAction = self.columnMenu.addAction(column.name)
                toggleAction.setCheckable(True)
                toggleAction.setChecked(not self.isColumnHidden(index))
                toggleAction.triggered.connect(
                    partial(self.__toggleColumn, index=index)
                )

        self.columnMenu.exec(self.mapToGlobal(position))
        self.columnMenu.clear()
