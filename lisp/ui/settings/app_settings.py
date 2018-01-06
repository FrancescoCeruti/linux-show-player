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

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QListWidget, QStackedWidget, \
    QDialogButtonBox

from lisp.ui.ui_utils import translate


class AppSettings(QDialog):

    SettingsWidgets = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setWindowTitle(translate('AppSettings', 'LiSP preferences'))

        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setMaximumSize(635, 530)
        self.setMinimumSize(635, 530)
        self.resize(635, 530)

        self.listWidget = QListWidget(self)
        self.listWidget.setGeometry(QtCore.QRect(5, 10, 185, 470))

        self.sections = QStackedWidget(self)
        self.sections.setGeometry(QtCore.QRect(200, 10, 430, 470))

        for widget, config in self.SettingsWidgets.items():
            widget = widget(parent=self)
            widget.resize(430, 465)
            widget.load_settings(config.copy())

            self.listWidget.addItem(translate('SettingsPageName', widget.Name))
            self.sections.addWidget(widget)

        if self.SettingsWidgets:
            self.listWidget.setCurrentRow(0)

        self.listWidget.currentItemChanged.connect(self._change_page)

        self.dialogButtons = QDialogButtonBox(self)
        self.dialogButtons.setGeometry(10, 495, 615, 30)
        self.dialogButtons.setStandardButtons(QDialogButtonBox.Cancel |
                                              QDialogButtonBox.Ok)

        self.dialogButtons.rejected.connect(self.reject)
        self.dialogButtons.accepted.connect(self.accept)

    def accept(self):
        for n in range(self.sections.count()):
            widget = self.sections.widget(n)

            config = AppSettings.SettingsWidgets[widget.__class__]
            config.update(widget.get_settings())
            config.write()

        return super().accept()

    @classmethod
    def register_settings_widget(cls, widget, configuration):
        """
        :type widget: Type[lisp.ui.settings.settings_page.SettingsPage]
        :type configuration: lisp.core.configuration.Configuration
        """
        if widget not in cls.SettingsWidgets:
            cls.SettingsWidgets[widget] = configuration

    @classmethod
    def unregister_settings_widget(cls, widget):
        cls.SettingsWidgets.pop(widget, None)

    def _change_page(self, current, previous):
        if not current:
            current = previous

        self.sections.setCurrentIndex(self.listWidget.row(current))
