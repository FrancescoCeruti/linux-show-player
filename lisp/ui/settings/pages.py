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

from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout

from lisp.core.qmeta import QABCMeta
from lisp.core.util import dict_merge
from lisp.ui.ui_utils import translate


class ABCSettingsPage(QWidget, metaclass=QABCMeta):
    Name = 'ABCSettingPage'


class SettingsPage(ABCSettingsPage):
    Name = 'SettingsPage'

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


class CuePageMixin:
    Name = 'CueSettingsPage'

    def __init__(self, cue_type):
        self.cue_type = cue_type


class CueSettingsPage(SettingsPage, CuePageMixin):

    def __init__(self, cue_type, **kwargs):
        super().__init__(cue_type=cue_type, **kwargs)


class ConfigurationPage(ABCSettingsPage):
    Name = 'ConfigurationPage'

    def __init__(self, config, **kwargs):
        """
        :param config: Configuration object to "edit"
        :type config: lisp.core.configuration.Configuration  
        """
        super().__init__(**kwargs)
        self.config = config

    @abstractmethod
    def applySettings(self):
        pass


class TabsMultiPage(QWidget):
    _PagesBaseClass = ABCSettingsPage

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())

        self.tabWidget = QTabWidget(parent=self)
        self.layout().addWidget(self.tabWidget)

        self._pages = []

    def page(self, index):
        return self._pages[index]

    def addPage(self, page):
        if isinstance(page, self._PagesBaseClass):
            self._pages.append(page)
            self.tabWidget.addTab(
                page, translate('SettingsPageName', page.Name))
        else:
            raise TypeError(
                'page must be an {}, not {}'.format(
                    self._PagesBaseClass.__name__,
                    type(page).__name__)
            )

    def removePage(self, index):
        self.tabWidget.removeTab(index)
        return self._pages.pop(index)

    def iterPages(self):
        yield from self._pages

    def pageIndex(self, page):
        return self._pages.index(page)


class TabsMultiSettingsPage(TabsMultiPage, SettingsPage):
    _PagesBaseClass = SettingsPage

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


class TabsMultiConfigurationPage(TabsMultiPage, ConfigurationPage):
    _PagesBaseClass = ConfigurationPage

    def applySettings(self):
        for page in self._pages:
            page.applySettings()
