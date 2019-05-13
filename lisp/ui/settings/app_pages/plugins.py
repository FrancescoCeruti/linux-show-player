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

from PyQt5.QtCore import QT_TRANSLATE_NOOP, Qt, QSize
from PyQt5.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QTextBrowser,
    QVBoxLayout,
)

from lisp import plugins
from lisp.ui.icons import IconTheme
from lisp.ui.settings.pages import SettingsPage


# TODO: add Enable/Disable options for plugins
class PluginsSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "Plugins")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.pluginsList = QListWidget(self)
        self.pluginsList.setIconSize(QSize(12, 12))
        self.pluginsList.setAlternatingRowColors(True)
        self.pluginsList.setSortingEnabled(True)
        self.pluginsList.setSelectionMode(QListWidget.SingleSelection)
        self.pluginsList.itemSelectionChanged.connect(self.__selection_changed)
        self.layout().addWidget(self.pluginsList)

        for name, plugin in plugins.PLUGINS.items():
            item = QListWidgetItem(plugin.Name)
            if plugins.is_loaded(name):
                item.setIcon(IconTheme.get("led-running"))
            elif not plugin.Config["_enabled_"]:
                item.setIcon(IconTheme.get("led-pause"))
            else:
                item.setIcon(IconTheme.get("led-error"))

            item.setData(Qt.UserRole, plugin)

            self.pluginsList.addItem(item)

        # Plugin description
        self.pluginDescription = QTextBrowser(self)
        self.layout().addWidget(self.pluginDescription)

        self.layout().setStretch(0, 3)
        self.layout().setStretch(1, 1)

        if self.pluginsList.count():
            self.pluginsList.setCurrentRow(0)

    def __selection_changed(self):
        item = self.pluginsList.currentItem()

        if item is not None:
            plugin = item.data(Qt.UserRole)
            html = "<b>Description: </b>{}".format(plugin.Description)
            html += "<br /><br />"
            html += "<b>Authors: </b>{}".format(", ".join(plugin.Authors))

            self.pluginDescription.setHtml(html)
        else:
            self.pluginDescription.setHtml(
                "<b>Description: </b><br /><br /><b>Authors: </b>"
            )
