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

from lisp.core.dicttree import DictNode
from lisp.ui.settings.pages_tree import TreeMultiSettingsPage, TreeSettingsModel
from lisp.ui.settings.settings_page import SettingsDialog, ConfigurationPage
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)

PageEntry = namedtuple('PageEntry', ('widget', 'config'))


class AppSettings(SettingsDialog):
    PagesRegistry = DictNode()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setWindowTitle(translate('AppSettings', 'LiSP preferences'))
        self.setWindowModality(QtCore.Qt.WindowModal)

    def _buildMainPage(self):
        self.model = TreeSettingsModel()
        mainPage = TreeMultiSettingsPage(self.model)

        for r_node in AppSettings.PagesRegistry.children:
            self._populateModel(QModelIndex(), r_node)

        mainPage.selectFirst()
        return mainPage

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

    @staticmethod
    def registerSettingsWidget(path, widget, config):
        """
        :param path: indicate the widget "position": 'category.sub.key'
        :type path: str
        :type widget: Type[lisp.ui.settings.settings_page.SettingsPage]
        :type config: lisp.core.configuration.Configuration
        """
        AppSettings.PagesRegistry.set(
            path, PageEntry(widget=widget, config=config))

    @staticmethod
    def unregisterSettingsWidget(path):
        """
        :param path: indicate the widget "position": 'category.sub.key'
        :type path: str
        """
        AppSettings.PagesRegistry.pop(path)
