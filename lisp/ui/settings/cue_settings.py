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

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QTabWidget, QDialogButtonBox

from lisp.core.class_based_registry import ClassBasedRegistry
from lisp.core.singleton import Singleton
from lisp.core.util import deep_update
from lisp.cues.cue import Cue
from lisp.ui.settings.settings_page import SettingsPage, CueSettingsPage
from lisp.ui.ui_utils import translate


class CueSettingsRegistry(ClassBasedRegistry, metaclass=Singleton):
    def add_item(self, item, ref_class=Cue):
        if not issubclass(item, SettingsPage):
            raise TypeError('item must be a SettingPage subclass, '
                            'not {0}'.format(item.__name__))
        if not issubclass(ref_class, Cue):
            raise TypeError('ref_class must be Cue or a subclass, not {0}'
                            .format(ref_class.__name__))

        return super().add_item(item, ref_class)

    def filter(self, ref_class=Cue):
        return super().filter(ref_class)

    def clear_class(self, ref_class=Cue):
        return super().filter(ref_class)


class CueSettings(QDialog):
    on_apply = QtCore.pyqtSignal(dict)

    def __init__(self, cue=None, cue_class=None, **kwargs):
        """

        :param cue: Target cue, or None for multi-editing
        :param cue_class: when cue is None, used to specify the reference class
        """
        super().__init__(**kwargs)

        if cue is not None:
            cue_class = cue.__class__
            cue_properties = deepcopy(cue.properties())
            self.setWindowTitle(cue_properties['name'])
        else:
            cue_properties = {}
            if cue_class is None:
                cue_class = Cue

        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setMaximumSize(635, 530)
        self.setMinimumSize(635, 530)
        self.resize(635, 530)

        self.sections = QTabWidget(self)
        self.sections.setGeometry(QtCore.QRect(5, 10, 625, 470))

        def sk(widget):
            # Sort-Key function
            return translate('SettingsPageName', widget.Name)

        for widget in sorted(CueSettingsRegistry().filter(cue_class), key=sk):
            if issubclass(widget, CueSettingsPage):
                settings_widget = widget(cue_class)
            else:
                settings_widget = widget()

            settings_widget.load_settings(cue_properties)
            settings_widget.enable_check(cue is None)
            self.sections.addTab(settings_widget,
                                 translate('SettingsPageName',
                                           settings_widget.Name))

            self.dialogButtons = QDialogButtonBox(self)
            self.dialogButtons.setGeometry(10, 490, 615, 30)
            self.dialogButtons.setStandardButtons(QDialogButtonBox.Cancel |
                                                  QDialogButtonBox.Ok |
                                                  QDialogButtonBox.Apply)

            self.dialogButtons.rejected.connect(self.reject)
            self.dialogButtons.accepted.connect(self.accept)
            apply = self.dialogButtons.button(QDialogButtonBox.Apply)
            apply.clicked.connect(self.apply)

    def load_settings(self, settings):
        for n in range(self.sections.count()):
            self.sections.widget(n).load_settings(settings)

    def get_settings(self):
        settings = {}

        for n in range(self.sections.count()):
            deep_update(settings, self.sections.widget(n).get_settings())

        return settings

    def apply(self):
        self.on_apply.emit(self.get_settings())

    def accept(self):
        self.apply()
        super().accept()
