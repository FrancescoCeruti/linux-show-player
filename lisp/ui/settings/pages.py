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

from abc import abstractmethod

from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QTreeView, \
    QGridLayout, QSizePolicy

from lisp.core.qmeta import QABCMeta
from lisp.core.util import dict_merge, typename
from lisp.ui.ui_utils import translate


class ABCPage(QWidget, metaclass=QABCMeta):
    Name = 'PageName'


class SettingsPage(ABCPage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @abstractmethod
    def loadSettings(self, settings):
        """Load existing settings value into the widget

        :param settings: the settings to load
        :type settings: dict
        """

    def getSettings(self):
        """Return the new settings values

        If an option (or a group) has been disabled by `enableCheck` their
        values should not be included.

        :rtype: dict
        """
        return {}

    def enableCheck(self, enabled):
        """Enable settings checks

        This should selectively enable/disable widgets in the page,
        usually you want to work with groups (QGroupBox).

        If an option (or a group) is disable the values should not be included
        in the return of `getSettings`

        :param enabled: if True enable checks
        :type enabled: bool
        """


class ConfigurationPage(ABCPage):
    def __init__(self, config, *args, **kwargs):
        """
        :param config: Configuration object to "edit"
        :type config: lisp.core.configuration.Configuration
        """
        super().__init__(*args, **kwargs)
        self.config = config

    @abstractmethod
    def applySettings(self):
        pass


class CuePageMixin:
    def __init__(self, cueType, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cueType = cueType


class CueSettingsPage(CuePageMixin, SettingsPage):
    def __init__(self, cueType, **kwargs):
        super().__init__(cueType=cueType, **kwargs)


class TabsMultiPage(ABCPage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())

        self.tabWidget = QTabWidget(parent=self)
        self.tabWidget.setFocusPolicy(Qt.StrongFocus)
        self.layout().addWidget(self.tabWidget)

        self._pages = []

    def page(self, index):
        return self._pages[index]

    def addPage(self, page):
        self._pages.append(page)
        self.tabWidget.addTab(page, translate('SettingsPageName', page.Name))

    def removePage(self, index):
        self.tabWidget.removeTab(index)
        return self._pages.pop(index)

    def iterPages(self):
        yield from self._pages

    def pageIndex(self, page):
        return self._pages.index(page)


class TabsMultiSettingsPage(TabsMultiPage):
    def loadSettings(self, settings):
        for page in self._pages:
            page.loadSettings(settings)

    def getSettings(self):
        settings = {}
        for page in self._pages:
            dict_merge(settings, page.getSettings())

        return settings

    def enableCheck(self, enabled):
        for page in self._pages:
            page.enableCheck(enabled)


class TabsMultiConfigurationPage(TabsMultiPage):
    def applySettings(self):
        for page in self._pages:
            page.applySettings()


class TreeMultiPagesWidget(ABCPage):
    def __init__(self, navModel, **kwargs):
        """
        :param navModel: The model that keeps all the pages-hierarchy
        :type navModel: lisp.ui.settings.pages_tree_model.PagesTreeModel
        """
        super().__init__(**kwargs)
        self.setLayout(QGridLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.navModel = navModel

        self.navWidget = QTreeView()
        self.navWidget.setHeaderHidden(True)
        self.navWidget.setModel(self.navModel)
        self.layout().addWidget(self.navWidget, 0, 0)

        self._currentWidget = QWidget()
        self.layout().addWidget(self._currentWidget, 0, 1)

        self.navWidget.selectionModel().selectionChanged.connect(
            self._changePage)

        self._resetStretch()

    def selectFirst(self):
        self.navWidget.setCurrentIndex(self.navModel.index(0, 0, QModelIndex()))

    def currentWidget(self):
        return self._currentWidget

    def _resetStretch(self):
        self.layout().setColumnStretch(0, 2)
        self.layout().setColumnStretch(1, 5)

    def _changePage(self, selected):
        if selected.indexes():
            self.layout().removeWidget(self._currentWidget)
            self._currentWidget.hide()
            self._currentWidget = selected.indexes()[0].internalPointer().page
            self._currentWidget.setSizePolicy(
                QSizePolicy.Ignored, QSizePolicy.Ignored)
            self._currentWidget.show()
            self.layout().addWidget(self._currentWidget, 0, 1)
            self._resetStretch()


class TreeMultiConfigurationWidget(TreeMultiPagesWidget):
    def applySettings(self):
        root = self.navModel.node(QModelIndex())
        for node in root.walk():
            if node.page is not None:
                node.page.applySettings()


class TreeMultiSettingsWidget(TreeMultiPagesWidget):
    def loadSettings(self, settings):
        root = self.navModel.node(QModelIndex())
        for node in root.walk():
            if node.page is not None:
                node.page.loadSettings(settings)

    def getSettings(self):
        settings = {}
        root = self.navModel.node(QModelIndex())
        for node in root.walk():
            if node.page is not None:
                dict_merge(settings, node.page.getSettings())

        return settings

    def enableCheck(self, enabled):
        root = self.navModel.node(QModelIndex())
        for node in root.walk():
            if node.page is not None:
                node.page.enableCheck(enabled)
