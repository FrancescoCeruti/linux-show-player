# This file is part of Linux Show Player
#
# Copyright 2017 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtCore import QT_TRANSLATE_NOOP, Qt, QAbstractTableModel, QModelIndex
from PyQt5.QtWidgets import (
    QTextBrowser,
    QVBoxLayout,
    QTableView,
    QHeaderView,
    QStyledItemDelegate,
)

from lisp import plugins
from lisp.core.plugin import PluginState
from lisp.ui.icons import IconTheme
from lisp.ui.qdelegates import BoolCheckBoxDelegate
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class PluginsSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "Plugins")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.pluginsModel = PluginModel()

        self.pluginsList = PluginsView(parent=self)  # QListWidget(self)
        self.pluginsList.setModel(self.pluginsModel)
        self.pluginsList.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Stretch
        )
        self.pluginsList.setAlternatingRowColors(True)
        self.pluginsList.selectionModel().selectionChanged.connect(
            self.__selection_changed
        )
        self.layout().addWidget(self.pluginsList)

        for name, plugin in plugins.get_plugins():
            self.pluginsModel.appendPlugin(plugin)

        # Plugin description
        self.pluginDescription = QTextBrowser(self)
        self.layout().addWidget(self.pluginDescription)

        self.layout().setStretch(0, 3)
        self.layout().setStretch(1, 1)

        if self.pluginsModel.rowCount():
            self.pluginsList.setCurrentIndex(self.pluginsModel.index(0, 0))

    def __selection_changed(self):
        plugin = self.pluginsList.currentIndex().data(Qt.UserRole)

        if plugin is not None:
            html = (
                f"<b>Description: </b>{plugin.Description}<br /><br />"
                f"<b>Authors: </b>{', '.join(plugin.Authors)}"
            )

            self.pluginDescription.setHtml(html)
        else:
            self.pluginDescription.setHtml(
                "<b>Description: </b><br /><br /><b>Authors: </b>"
            )


class PluginModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()

        self.plugins = []
        self.columns = [
            translate("PluginsSettings", "Plugin"),
            translate("PluginsSettings", "Enabled"),
        ]

    def appendPlugin(self, plugin):
        row = len(self.plugins) - 1

        self.beginInsertRows(QModelIndex(), row, row)
        self.plugins.append(plugin)
        self.endInsertRows()

    def rowCount(self, parent=QModelIndex()):
        return len(self.plugins)

    def columnCount(self, parent=QModelIndex()):
        return len(self.columns)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section < len(self.columns):
                return self.columns[section]
            else:
                return section + 1

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            column = index.column()
            plugin = self.plugins[index.row()]

            # Column-independent values
            if role == Qt.TextAlignmentRole:
                return Qt.AlignLeft | Qt.AlignVCenter
            elif role == Qt.ToolTipRole:
                return plugin.status_text()
            elif role == Qt.UserRole:
                return plugin

            # Column-dependent values
            if column == 0:
                if role == Qt.DisplayRole:
                    return plugin.Name
                elif role == Qt.DecorationRole:
                    return IconTheme.get(plugin_status_icon(plugin))
            elif column == 1:
                enabled = plugin.is_enabled()
                if role in (Qt.DisplayRole, Qt.EditRole):
                    return enabled

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            row = index.row()
            column = index.column()
            plugin = self.plugins[row]
            if column == 1 and isinstance(value, bool):
                if plugin.is_enabled() != value:
                    plugin.set_enabled(value)
                    self.dataChanged.emit(
                        self.index(row, 0),
                        self.index(row, column),
                        [Qt.DisplayRole, Qt.EditRole],
                    )

                    return True

        return False

    def flags(self, index):
        column = index.column()
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if column == 1 and not self.plugins[column].CorePlugin:
            flags |= Qt.ItemIsEditable

        return flags


class PluginsView(QTableView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.delegates = [
            QStyledItemDelegate(),
            BoolCheckBoxDelegate(),
        ]

        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)

        self.setShowGrid(False)
        self.setAlternatingRowColors(True)

        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )

        self.verticalHeader().setVisible(False)
        self.verticalHeader().sectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(24)
        self.verticalHeader().setHighlightSections(False)

        for column, delegate in enumerate(self.delegates):
            self.setItemDelegateForColumn(column, delegate)


def plugin_status_icon(plugin):
    if plugin.State & PluginState.Error:
        return "led-error"
    elif plugin.State & PluginState.Warning:
        return "led-pause"
    elif plugin.State & PluginState.Loaded:
        return "led-running"

    return "led-off"
