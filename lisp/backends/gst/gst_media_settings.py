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

from copy import deepcopy

from PyQt5.QtWidgets import QGridLayout, QListWidget, QPushButton, \
    QListWidgetItem

from lisp.backends.gst.gst_pipe_edit import GstPipeEditDialog
from lisp.backends.gst.settings import pages_by_element_name
from lisp.ui.settings.settings_page import SettingsPage


class GstMediaSettings(SettingsPage):
    Name = 'Media Settings'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QGridLayout())

        self._pages = []
        self._current_page = None
        self._settings = {}
        self._check = False

        self.listWidget = QListWidget(self)
        self.layout().addWidget(self.listWidget, 0, 0)

        self.pipeButton = QPushButton('Change Pipe', self)
        self.layout().addWidget(self.pipeButton, 1, 0)

        self.layout().setColumnStretch(0, 2)
        self.layout().setColumnStretch(1, 5)

        self.listWidget.currentItemChanged.connect(self.__change_page)
        self.pipeButton.clicked.connect(self.__edit_pipe)

    def load_settings(self, settings):
        settings = settings.get('_media_', {})
        # Create a local copy of the configuration
        self._settings = deepcopy(settings)

        # Create the widgets
        pages = pages_by_element_name()
        for element in settings.get('pipe', ()):
            page = pages.get(element)

            if page is not None and issubclass(page, SettingsPage):
                page = page(parent=self)
                page.load_settings(
                    settings.get('elements', {})
                    .get(element, page.ELEMENT.properties_defaults()))
                page.setVisible(False)
                self._pages.append(page)

                item = QListWidgetItem(page.NAME)
                self.listWidget.addItem(item)

            self.listWidget.setCurrentRow(0)

    def get_settings(self):
        settings = {'elements': {}}

        for page in self._pages:
            page_settings = page.get_settings()

            if page_settings:
                settings['elements'][page.ELEMENT.Name] = page_settings

        # The pipeline is returned only if check is disabled
        if not self._check:
            settings['pipe'] = self._settings['pipe']

        return {'_media_': settings}

    def enable_check(self, enabled):
        self._check = enabled
        for page in self._pages:
            page.enable_check(enabled)

    def __change_page(self, current, previous):
        if current is None:
            current = previous

        if self._current_page is not None:
            self.layout().removeWidget(self._current_page)
            self._current_page.hide()

        self._current_page = self._pages[self.listWidget.row(current)]
        self._current_page.show()
        self.layout().addWidget(self._current_page, 0, 1, 2, 1)

    def __edit_pipe(self):
        # Backup the settings
        self._settings = self.get_settings()['_media_']

        # Show the dialog
        dialog = GstPipeEditDialog(self._settings.get('pipe', ()), parent=self)

        if dialog.exec_() == dialog.Accepted:
            # Reset the view
            self.listWidget.clear()
            if self._current_page is not None:
                self.layout().removeWidget(self._current_page)
                self._current_page.hide()
            self._current_page = None
            self._pages.clear()

            # Reload with the new pipeline
            self._settings['pipe'] = dialog.get_pipe()

            self.load_settings({'_media_': self._settings})
            self.enable_check(self._check)
