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
from PyQt5.QtWidgets import QVBoxLayout, QDialogButtonBox, QDialog

from lisp.core.dicttree import DictNode
from lisp.core.util import typename
from lisp.ui.settings.pages import ConfigurationPage, TreeMultiConfigurationWidget
from lisp.ui.settings.pages_tree_model import PagesTreeModel
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)

PageEntry = namedtuple('PageEntry', ('page', 'config'))


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

        self.model = PagesTreeModel()
        for r_node in AppConfigurationDialog.PagesRegistry.children:
            self._populateModel(QModelIndex(), r_node)

        self.mainPage = TreeMultiConfigurationWidget(self.model)
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
            page = r_parent.value.page
            config = r_parent.value.config
        else:
            page = None
            config = None

        try:
            if page is None:
                # The current node have no page, use the parent model-index
                # as parent for it's children
                mod_index = m_parent
            elif issubclass(page, ConfigurationPage):
                mod_index = self.model.addPage(page(config), parent=m_parent)
            else:
                mod_index = self.model.addPage(page(), parent=m_parent)
        except Exception:
            if not isinstance(page, type):
                page_name = 'NoPage'
            elif issubclass(page, ConfigurationPage):
                page_name = page.Name
            else:
                page_name = page.__name__

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
    def registerSettingsPage(path, page, config):
        """
        :param path: indicate the page "position": 'category.sub.key'
        :type path: str
        :type page: Type[lisp.ui.settings.settings_page.ConfigurationPage]
        :type config: lisp.core.configuration.Configuration
        """
        if issubclass(page, ConfigurationPage):
            AppConfigurationDialog.PagesRegistry.set(
                path, PageEntry(page=page, config=config))
        else:
            raise TypeError(
                'AppConfiguration pages must be ConfigurationPage(s), not {}'
                    .format(typename(page))
            )

    @staticmethod
    def unregisterSettingsPage(path):
        """
        :param path: indicate the page "position": 'category.sub.key'
        :type path: str
        """
        AppConfigurationDialog.PagesRegistry.pop(path)
