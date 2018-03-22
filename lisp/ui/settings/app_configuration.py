# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

import logging
from collections import namedtuple

from PyQt5 import QtCore
from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QVBoxLayout, QDialogButtonBox, QDialog, QTreeView, \
    QHBoxLayout, QWidget

from lisp.core.dicttree import DictNode
from lisp.ui.settings.pages import ConfigurationPage
from lisp.ui.settings.pages_tree_model import SettingsPagesTreeModel
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)

PageEntry = namedtuple('PageEntry', ('widget', 'config'))


class AppConfigurationDialog(QDialog):
    PagesRegistry = DictNode()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setWindowTitle(translate('AppConfiguration', 'LiSP preferences'))
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.setMaximumSize(640, 510)
        self.setMinimumSize(640, 510)
        self.resize(640, 510)
        self.setLayout(QVBoxLayout())

        self.model = SettingsPagesTreeModel()
        for r_node in AppConfigurationDialog.PagesRegistry.children:
            self._populateModel(QModelIndex(), r_node)

        self.mainPage = TreeMultiSettingsWidget(self.model)
        self.mainPage.selectFirst()
        self.layout().addWidget(self.mainPage)

        self.dialogButtons = QDialogButtonBox(self)
        self.dialogButtons.setStandardButtons(
            QDialogButtonBox.Cancel |
            QDialogButtonBox.Apply |
            QDialogButtonBox.Ok
        )
        self.layout().addWidget(self.dialogButtons)

        self.dialogButtons.button(QDialogButtonBox.Cancel).clicked.connect(
            self.reject)
        self.dialogButtons.button(QDialogButtonBox.Apply).clicked.connect(
            self.applySettings)
        self.dialogButtons.button(QDialogButtonBox.Ok).clicked.connect(
            self.__onOk)

    def applySettings(self):
        self.mainPage.applySettings()

    def _populateModel(self, m_parent, r_parent):
        if r_parent.value is not None:
            widget = r_parent.value.widget
            config = r_parent.value.config
        else:
            widget = None
            config = None

        try:
            if widget is None:
                # The current node have no widget, use the parent model-index
                # as parent for it's children
                mod_index = m_parent
            elif issubclass(widget, ConfigurationPage):
                mod_index = self.model.addPage(widget(config), parent=m_parent)
            else:
                mod_index = self.model.addPage(widget(), parent=m_parent)
        except Exception:
            if not isinstance(widget, type):
                page_name = 'NoPage'
            elif issubclass(widget, ConfigurationPage):
                page_name = widget.Name
            else:
                page_name = widget.__name__

            logger.warning(
                'Cannot load configuration page: "{}" ({})'.format(
                    page_name, r_parent.path()), exc_info=True)
        else:
            for r_node in r_parent.children:
                self._populateModel(mod_index, r_node)

    def __onOk(self):
        self.applySettings()
        self.accept()

    @staticmethod
    def registerSettingsWidget(path, widget, config):
        """
        :param path: indicate the widget "position": 'category.sub.key'
        :type path: str
        :type widget: Type[lisp.ui.settings.settings_page.SettingsPage]
        :type config: lisp.core.configuration.Configuration
        """
        AppConfigurationDialog.PagesRegistry.set(
            path, PageEntry(widget=widget, config=config))

    @staticmethod
    def unregisterSettingsWidget(path):
        """
        :param path: indicate the widget "position": 'category.sub.key'
        :type path: str
        """
        AppConfigurationDialog.PagesRegistry.pop(path)


class TreeMultiSettingsWidget(QWidget):
    def __init__(self, navModel, **kwargs):
        """
        :param navModel: The model that keeps all the pages-hierarchy
        :type navModel: SettingsPagesTreeModel
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
            if node.widget is not None:
                node.widget.applySettings()

    def _changePage(self, selected):
        if selected.indexes():
            self.layout().removeWidget(self._currentWidget)
            self._currentWidget.hide()
            self._currentWidget = selected.indexes()[0].internalPointer().widget
            self._currentWidget.show()
            self.layout().addWidget(self._currentWidget)
            self.layout().setStretch(0, 2)
            self.layout().setStretch(1, 5)
