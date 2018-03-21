# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2018 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtCore import QAbstractItemModel, Qt, QModelIndex
from PyQt5.QtWidgets import QTreeView, QHBoxLayout, QWidget

from lisp.ui.settings.settings_page import ABCSettingsPage


class TreeSettingsNode:
    """
    :type parent: TreeSettingsNode
    :type _children: list[TreeSettingsNode]
    """
    def __init__(self, page):
        self.parent = None
        self.settingsPage = page

        self._children = []

    def addChild(self, child):
        self._children.append(child)
        child.parent = self

    def removeChild(self, position):
        if 0 < position < len(self._children):
            child = self._children.pop(position)
            child.parent = None

            return True

        return False

    def child(self, row):
        return self._children[row]

    def childIndex(self, child):
        return self._children.index(child)

    def childCount(self):
        return len(self._children)

    def row(self):
        if self.parent is not None:
            return self.parent.childIndex(self)

    def walk(self):
        for child in self._children:
            yield child
            yield from child.walk()


class TreeSettingsModel(QAbstractItemModel):
    PageRole = Qt.UserRole + 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._root = TreeSettingsNode(None)

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return parent.internalPointer().childCount()
        else:
            return self._root.childCount()

    def columnCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            node = index.internalPointer()
            if role == Qt.DisplayRole:
                return node.settingsPage.Name
            elif role == TreeSettingsModel.PageRole:
                return node.settingsPage

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        return None

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def node(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node is not None:
                return node

        return self._root

    def parent(self, index):
        parent = self.node(index).parent
        if parent is self._root:
            return QModelIndex()

        return self.createIndex(parent.row(), 0, parent)

    def index(self, row, column, parent=QModelIndex()):
        child = self.node(parent).child(row)
        if child is not None:
            return self.createIndex(row, column, child)

        return QModelIndex()

    def pageIndex(self, page, parent=QModelIndex()):
        parentNode = self.node(parent)
        for row in range(parentNode.childCount()):
            if parentNode.child(row).settingsPage is page:
                return self.index(row, 0, parent)

        return QModelIndex()

    def addPage(self, page, parent=QModelIndex()):
        if isinstance(page, ABCSettingsPage):
            parentNode = self.node(parent)
            position = parentNode.childCount()

            self.beginInsertRows(parent, position, position)
            node = TreeSettingsNode(page)
            parentNode.addChild(node)
            self.endInsertRows()

            return self.index(position, 0, parent)
        else:
            raise TypeError(
                'TreeSettingsModel page must be an ABCSettingsPage, not {}'
                    .format(type(page).__name__)
            )

    def removePage(self, row, parent=QModelIndex()):
        parentNode = self.node(parent)

        if row < parentNode.childCount():
            self.beginRemoveRows(parent, row, row)
            parentNode.removeChild(row)
            self.endRemoveRows()


class TreeMultiSettingsPage(ABCSettingsPage):
    def __init__(self, navModel, **kwargs):
        """
        :param navModel: The model that keeps all the pages-hierarchy
        :type navModel: TreeSettingsModel
        """
        super().__init__(**kwargs)
        self.setLayout(QHBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.navModel = navModel

        self.navWidget = QTreeView()
        self.navWidget.setHeaderHidden(True)
        self.navWidget.setModel(self.navModel)
        self.layout().addWidget(self.navWidget)

        self._currentWidget = QWidget()
        self.layout().addWidget(self._currentWidget)

        self.layout().setStretch(0, 2)
        self.layout().setStretch(1, 5)

        self.navWidget.selectionModel().selectionChanged.connect(
            self._changePage)

    def selectFirst(self):
        self.navWidget.setCurrentIndex(self.navModel.index(0, 0, QModelIndex()))

    def currentWidget(self):
        return self._currentWidget

    def applySettings(self):
        root = self.navModel.node(QModelIndex())
        for node in root.walk():
            if node.settingsPage is not None:
                node.settingsPage.applySettings()

    def _changePage(self, selected):
        if selected.indexes():
            self.layout().removeWidget(self._currentWidget)
            self._currentWidget.hide()
            self._currentWidget = selected.indexes()[0].internalPointer().settingsPage
            self._currentWidget.show()
            self.layout().addWidget(self._currentWidget)
            self.layout().setStretch(0, 2)
            self.layout().setStretch(1, 5)
