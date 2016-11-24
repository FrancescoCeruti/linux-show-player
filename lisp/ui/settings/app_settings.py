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

from lisp.core.util import deep_update
from lisp.ui.ui_utils import translate


class AppSettings(QDialog):

    SettingsWidgets = []

    def __init__(self, conf, **kwargs):
        super().__init__(**kwargs)

        self.conf = conf
        self.setWindowTitle(translate('AppSettings', 'LiSP preferences'))

        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setMaximumSize(635, 530)
        self.setMinimumSize(635, 530)
        self.resize(635, 530)

        self.listWidget = QListWidget(self)
        self.listWidget.setGeometry(QtCore.QRect(5, 10, 185, 470))

        self.sections = QStackedWidget(self)
        self.sections.setGeometry(QtCore.QRect(200, 10, 430, 470))

        for widget in self.SettingsWidgets:
            widget = widget(parent=self)
            widget.resize(430, 465)
            widget.load_settings(self.conf)

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

    def get_configuraton(self):
        conf = {}

        for n in range(self.sections.count()):
            widget = self.sections.widget(n)
            newconf = widget.get_settings()
            deep_update(conf, newconf)

        return conf

    @classmethod
    def register_settings_widget(cls, widget):
        if widget not in cls.SettingsWidgets:
            cls.SettingsWidgets.append(widget)

    @classmethod
    def unregister_settings_widget(cls, widget):
        if widget in cls.SettingsWidgets:
            cls.SettingsWidgets.remove(widget)

    def _change_page(self, current, previous):
        if not current:
            current = previous

        self.sections.setCurrentIndex(self.listWidget.row(current))
