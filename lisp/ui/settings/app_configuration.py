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

import logging
from collections import namedtuple

from PyQt5 import QtCore
from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QVBoxLayout, QDialogButtonBox, QDialog

from lisp.core.collections.dicttree import DictNode
from lisp.ui.ui_utils import translate
from lisp.ui.widgets.pagestreewidget import PagesTreeModel, PagesTreeWidget

logger = logging.getLogger(__name__)

PageEntry = namedtuple("PageEntry", ("page", "config"))


class AppConfigurationDialog(QDialog):
    PagesRegistry = DictNode()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setWindowTitle(translate("AppConfiguration", "LiSP preferences"))
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.setMinimumSize(800, 510)
        self.resize(800, 510)
        self.setLayout(QVBoxLayout())

        self.configurations = {}

        self.model = PagesTreeModel(tr_context="SettingsPageName")
        for page_node in AppConfigurationDialog.PagesRegistry.children:
            self._populateModel(QModelIndex(), page_node)

        self.mainPage = PagesTreeWidget(self.model)
        self.mainPage.selectFirst()
        self.layout().addWidget(self.mainPage)

        self.dialogButtons = QDialogButtonBox(self)
        self.dialogButtons.setStandardButtons(
            QDialogButtonBox.Cancel
            | QDialogButtonBox.Apply
            | QDialogButtonBox.Ok
        )
        self.layout().addWidget(self.dialogButtons)

        self.dialogButtons.button(QDialogButtonBox.Cancel).clicked.connect(
            self.reject
        )
        self.dialogButtons.button(QDialogButtonBox.Apply).clicked.connect(
            self.applySettings
        )
        self.dialogButtons.button(QDialogButtonBox.Ok).clicked.connect(
            self.__onOk
        )

    def applySettings(self):
        for conf, pages in self.configurations.items():
            for page in pages:
                conf.update(page.getSettings())

            conf.write()

    def _populateModel(self, model_parent, page_parent):
        if page_parent.value is not None:
            page_class = page_parent.value.page
            config = page_parent.value.config
        else:
            page_class = None
            config = None

        try:
            if page_class is None:
                # The current node have no page, use the parent model-index
                # as parent for it's children
                model_index = model_parent
            else:
                page_instance = page_class()
                page_instance.loadSettings(config)
                model_index = self.model.addPage(
                    page_instance, parent=model_parent
                )

                # Keep track of configurations and corresponding pages
                self.configurations.setdefault(config, []).append(page_instance)
        except Exception:
            if not isinstance(page_class, type):
                page_name = "InvalidPage"
            else:
                page_name = getattr(page_class, "Name", page_class.__name__)

            logger.warning(
                translate(
                    "AppConfigurationWarning",
                    'Cannot load configuration page: "{}" ({})',
                ).format(page_name, page_parent.path()),
                exc_info=True,
            )
        else:
            for page_node in page_parent.children:
                self._populateModel(model_index, page_node)

    def __onOk(self):
        self.applySettings()
        self.accept()

    @staticmethod
    def registerSettingsPage(path, page, config):
        """
        :param path: indicate the page "position": 'category.sub.key'
        :type path: str
        :type page: type
        :type config: lisp.core.configuration.Configuration
        """
        AppConfigurationDialog.PagesRegistry.set(
            path, PageEntry(page=page, config=config)
        )

    @staticmethod
    def unregisterSettingsPage(path):
        """
        :param path: indicate the page "position": 'category.sub.key'
        :type path: str
        """
        AppConfigurationDialog.PagesRegistry.pop(path)
