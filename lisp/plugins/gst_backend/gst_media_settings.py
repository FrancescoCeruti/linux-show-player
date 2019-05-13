# This file is part of Linux Show Player
#
# Copyright 2018 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtCore import QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import (
    QGridLayout,
    QListWidget,
    QPushButton,
    QListWidgetItem,
    QSizePolicy,
)

from lisp.plugins.gst_backend.gst_pipe_edit import GstPipeEditDialog
from lisp.plugins.gst_backend.settings import pages_by_element
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class GstMediaSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "Media Settings")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QGridLayout())

        self._pages = []
        self._current_page = None
        self._settings = {}
        self._check = False

        self.listWidget = QListWidget(self)
        self.layout().addWidget(self.listWidget, 0, 0)

        self.pipeButton = QPushButton(
            translate("GstMediaSettings", "Change Pipeline"), self
        )
        self.layout().addWidget(self.pipeButton, 1, 0)

        self.layout().setColumnStretch(0, 2)
        self.layout().setColumnStretch(1, 5)

        self.listWidget.currentItemChanged.connect(self.__change_page)
        self.pipeButton.clicked.connect(self.__edit_pipe)

    def loadSettings(self, settings):
        settings = settings.get("media", {})
        # Create a local copy of the configuration
        self._settings = deepcopy(settings)

        # Create the widgets
        pages = pages_by_element()
        for element in settings.get("pipe", ()):
            page = pages.get(element)

            if page is not None and issubclass(page, SettingsPage):
                page = page(parent=self)
                page.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
                page.loadSettings(
                    settings.get("elements", {}).get(
                        element, page.ELEMENT.class_defaults()
                    )
                )
                page.setVisible(False)
                self._pages.append(page)

                item = QListWidgetItem(translate("MediaElementName", page.Name))
                self.listWidget.addItem(item)

            self.listWidget.setCurrentRow(0)

    def getSettings(self):
        settings = {"elements": {}}

        for page in self._pages:
            page_settings = page.getSettings()

            if page_settings:
                settings["elements"][page.ELEMENT.__name__] = page_settings

        # The pipeline is returned only if check is disabled
        if not self._check:
            settings["pipe"] = self._settings["pipe"]

        return {"media": settings}

    def enableCheck(self, enabled):
        self._check = enabled
        for page in self._pages:
            page.enableCheck(enabled)

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
        self._settings = self.getSettings()["media"]

        # Show the dialog
        dialog = GstPipeEditDialog(self._settings.get("pipe", ()), parent=self)

        if dialog.exec() == dialog.Accepted:
            # Reset the view
            self.listWidget.clear()
            if self._current_page is not None:
                self.layout().removeWidget(self._current_page)
                self._current_page.hide()
            self._current_page = None
            self._pages.clear()

            # Reload with the new pipeline
            self._settings["pipe"] = dialog.get_pipe()

            self.loadSettings({"media": self._settings})
            self.enableCheck(self._check)
