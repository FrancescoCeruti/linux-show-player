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

from PyQt5.QtCore import QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import QHBoxLayout, QTabWidget

from lisp.plugins.controller import protocols
from lisp.ui.settings.settings_page import CueSettingsPage
from lisp.ui.ui_utils import translate


class ControllerSettings(CueSettingsPage):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'Cue Control')

    def __init__(self, cue_class, **kwargs):
        super().__init__(cue_class, **kwargs)
        self.setLayout(QHBoxLayout())

        self._pages = []

        self.tabWidget = QTabWidget(self)
        self.layout().addWidget(self.tabWidget)

        for page in protocols.ProtocolsSettingsPages:
            page_widget = page(cue_class, parent=self)

            self.tabWidget.addTab(page_widget,
                                  translate('SettingsPageName', page.Name))
            self._pages.append(page_widget)

        self.tabWidget.setCurrentIndex(0)

    def enable_check(self, enabled):
        for page in self._pages:
            page.enable_check(enabled)

    def get_settings(self):
        settings = {}
        for page in self._pages:
            settings.update(page.get_settings())

        return {'controller': settings}

    def load_settings(self, settings):
        settings = settings.get('controller', {})

        for page in self._pages:
            page.load_settings(settings)
