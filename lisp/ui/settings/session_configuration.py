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
from lisp.ui.settings.pages import SettingsPage, TreeMultiSettingsWidget
from lisp.ui.widgets.pagestreewidget import PagesTreeModel
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)

PageEntry = namedtuple('PageEntry', ('page', 'plugin'))


class SessionConfigurationDialog(QDialog):
    PagesRegistry = DictNode()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setWindowTitle(translate('SessionConfiguration', 'Session preferences'))
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.setMaximumSize(800, 510)
        self.setMinimumSize(800, 510)
        self.resize(800, 510)
        self.setLayout(QVBoxLayout())

        self._confsMap = {}
        self.model = PagesTreeModel()
        for r_node in SessionConfigurationDialog.PagesRegistry.children:
            self._populateModel(QModelIndex(), r_node)

        self.mainPage = TreeMultiSettingsWidget(self.model)
        if len(self.PagesRegistry.children):
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
        for plugin, config in self._confsMap.items():
            settings = config['conf']
            for page in config['pages']:
                settings.update(page.getSettings())
            plugin.WriteSessionConfig(settings)

    def _populateModel(self, m_parent, r_parent):
        if r_parent.value is not None:
            page_class = r_parent.value.page
            config = r_parent.value.plugin.SessionConfig
        else:
            page_class = None
            config = None

        try:
            if page_class is None:
                # The current node have no page, use the parent model-index
                # as parent for it's children
                mod_index = m_parent
            else:
                page_instance = page_class()
                page_instance.loadSettings(config)
                mod_index = self.model.addPage(page_instance, parent=m_parent)

                # Keep track of configurations and corresponding pages
                self._confsMap.setdefault(r_parent.value.plugin,
                                          {
                                            "pages": [],
                                            "conf": config
                                          })
                self._confsMap[r_parent.value.plugin]['pages'].append(page_instance)
        except Exception:
            if not isinstance(page_class, type):
                page_name = 'InvalidPage'
            else:
                page_name = getattr(page_class, 'Name', page_class.__name__)

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
    def registerSettingsPage(path, page, plugin):
        """
        :param path: indicate the page "position": 'category.sub.key'
        :type path: str
        :type page: Type[lisp.ui.settings.settings_page.SettingsPage]
        :type plugin_config: lisp.core.configuration.Configuration
        """
        if issubclass(page, SettingsPage):
            SessionConfigurationDialog.PagesRegistry.set(
                path, PageEntry(page=page, plugin=plugin))
        else:
            raise TypeError(
                'SessionConfiguration pages must be SettingsPage(s), not {}'
                    .format(typename(page))
            )

    @staticmethod
    def unregisterSettingsPage(path):
        """
        :param path: indicate the page "position": 'category.sub.key'
        :type path: str
        """
        SessionConfigurationDialog.PagesRegistry.pop(path)
