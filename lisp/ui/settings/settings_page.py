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

from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QDialogButtonBox, \
    QTabWidget

from lisp.core.qmeta import QABCMeta
from lisp.ui.ui_utils import translate


class ABCSettingsPage(QWidget, metaclass=QABCMeta):
    Name = 'SettingPage'

    @abstractmethod
    def applySettings(self):
        pass


class SettingsPage(QWidget):
    def enableCheck(self, enabled):
        """Enable options check"""

    def getSettings(self):
        """Return the current settings."""
        return {}

    def loadSettings(self, settings):
        """Load the settings."""


class CueSettingsPage(SettingsPage):
    Name = 'Cue page'

    def __init__(self, cue_class, **kwargs):
        super().__init__(**kwargs)
        self._cue_class = cue_class


class DummySettingsPage(ABCSettingsPage):

    def applySettings(self):
        pass


class ConfigurationPage(ABCSettingsPage):
    def __init__(self, config, **kwargs):
        """
        :param config: Configuration object to "edit"
        :type config: lisp.core.configuration.Configuration  
        """
        super().__init__(**kwargs)
        self.config = config


class TabsMultiSettingsPage(QTabWidget, ABCSettingsPage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._pages = []

    def page(self, index):
        return self._pages[index]

    def addPage(self, page):
        if isinstance(page, ABCSettingsPage):
            self._pages.append(page)
            self.addTab(page, translate('SettingsPageName', page.Name))
        else:
            raise TypeError(
                'page must be an ABCSettingsPage, not {}'
                    .format(type(page).__name__)
            )

    def removePage(self, index):
        return self._pages.pop(index)

    def iterPages(self):
        yield from self._pages

    def pageIndex(self, page):
        return self._pages.index(page)

    def applySettings(self):
        for page in self._pages:
            page.applySettings()


class SettingsDialog(QDialog, ABCSettingsPage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.setMaximumSize(640, 510)
        self.setMinimumSize(640, 510)
        self.resize(640, 510)

        self.mainPage = self._buildMainPage()
        self.layout().addWidget(self.mainPage)

        self.dialogButtons = QDialogButtonBox(self)
        self.dialogButtons.setStandardButtons(
            QDialogButtonBox.Cancel
            | QDialogButtonBox.Apply
            | QDialogButtonBox.Ok
        )
        self.layout().addWidget(self.dialogButtons)

        self.dialogButtons.button(QDialogButtonBox.Apply).clicked.connect(
            self.applySettings)
        self.dialogButtons.button(QDialogButtonBox.Ok).clicked.connect(
            self.__onOK)
        self.dialogButtons.button(QDialogButtonBox.Cancel).clicked.connect(
            self.__onCancel)

    def applySettings(self):
        self.mainPage.applySettings()

    @abstractmethod
    def _buildMainPage(self):
        """:rtype: ABCSettingsPage"""
        pass

    def __onOK(self):
        self.applySettings()
        self.accept()

    def __onCancel(self):
        self.reject()
