# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2015 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtWidgets import QAction, QMenu, qApp

from lisp.core.actions_handler import MainActionsHandler
from lisp.core.signal import Signal
from lisp.cues.cue import Cue
from lisp.layouts.cue_layout_actions import ConfigureAction, \
    MultiConfigureAction
from lisp.ui.mainwindow import MainWindow
from lisp.ui.settings.cue_settings import CueSettings
from lisp.ui.settings.section import SettingsSection


class CueLayout():

    # Layout name
    NAME = 'Base'
    # Layout info (html)
    DESCRIPTION = '<p>No description</p>'

    _settings_sections = {}
    _context_items = {}

    def __init__(self, cue_model):
        self._cue_model = cue_model

        self.cue_executed = Signal()    # After a cue is executed
        self.focus_changed = Signal()   # After the focused cue is changed
        self.key_pressed = Signal()     # After a key is pressed

    @property
    def cue_model(self):
        """:rtype: lisp.model_view.cue_model.CueModel"""
        return self._cue_model

    @property
    @abstractmethod
    def model_adapter(self):
        """:rtype: lisp.model_view.model_adapter.ModelAdapter"""

    @classmethod
    def add_context_item(cls, item, cue_class=Cue):
        if cue_class not in cls._context_items:
            cls._context_items[cue_class] = [item]
        else:
            cls._context_items[cue_class].append(item)

    @classmethod
    def add_context_separator(cls, cue_class=Cue):
        separator = QAction(None)
        separator.setSeparator(True)

        if cue_class not in cls._context_items:
            cls._context_items[cue_class] = [separator]
        else:
            cls._context_items[cue_class].append(separator)

        return separator

    @classmethod
    def add_settings_section(cls, section, cue_class=Cue):
        if issubclass(section, SettingsSection):
            if cue_class not in cls._settings_sections:
                cls._settings_sections[cue_class] = [section]
            elif section not in cls._settings_sections[cue_class]:
                cls._settings_sections[cue_class].append(section)

    @abstractmethod
    def deselect_all(self):
        """Deselect all the cues"""

    @abstractmethod
    def finalize(self):
        """Destroy all the layout elements"""

    def edit_cue(self, cue):
        widgets = []
        for cue_class in self._settings_sections:
            if issubclass(cue.__class__, cue_class):
                widgets.extend(self._settings_sections[cue_class])

        if widgets:
            widgets.sort(key=lambda w: w.Name)

            edit_ui = CueSettings(widgets, cue, parent=MainWindow())

            def on_apply(settings):
                action = ConfigureAction(settings, cue)
                MainActionsHandler().do_action(action)

            edit_ui.on_apply.connect(on_apply)
            edit_ui.exec_()

    def edit_selected_cues(self):
        cues = self.get_selected_cues()

        if cues:
            # Obtains the most generic class between the selected cues
            generic = cues[0].__class__
            for cue in cues:
                if issubclass(generic, cue.__class__):
                    generic = cue.__class__
                elif not issubclass(cue.__class__, generic):
                    generic = Cue
                    break

            # Obtains the available settings-widgets for the "generic" class
            widgets = []
            for cue_class in self._settings_sections:
                if issubclass(generic, cue_class):
                    widgets.extend(self._settings_sections[cue_class])
            widgets.sort(key=lambda w: w.Name)

            edit_ui = CueSettings(widgets, check=True)

            def on_apply(settings):
                action = MultiConfigureAction(settings, cues)
                MainActionsHandler().do_action(action)

            edit_ui.on_apply.connect(on_apply)
            edit_ui.exec_()

    @abstractmethod
    def get_context_cue(self):
        """Return the last cue in the context-menu scope, or None"""
        return None

    @abstractmethod
    def get_selected_cues(self, cue_class=Cue):
        """Return an "ordered" list of all selected cues"""
        return []

    @abstractmethod
    def invert_selection(self):
        """Invert selection"""

    @classmethod
    def remove_context_item(cls, item):
        for key in cls._context_items:
            cls._context_items[key] = [i for i in cls._context_items[key] if i != item]

    @classmethod
    def remove_settings_section(cls, section):
        for key in cls._settings_sections:
            cls._settings_sections[key] = [s for s in cls._settings_sections[key] if s != section]

    @abstractmethod
    def select_all(self):
        """Select all the cues"""

    def show_context_menu(self, position):
        items = []
        cue = self.get_context_cue()
        for class_ in sorted(self._context_items.keys(), key=lambda i: str(i)):
            if isinstance(cue, class_):
                items.extend(self._context_items[class_])

        if items:
            menu = QMenu(self)

            for item in items:
                if isinstance(item, QAction):
                    menu.addAction(item)
                elif isinstance(item, QMenu):
                    menu.addMenu(item)

            menu.move(position)
            menu.show()

            # Adjust the menu position
            desktop = qApp.desktop().availableGeometry()
            menu_rect = menu.geometry()

            if menu_rect.bottom() > desktop.bottom():
                menu.move(menu.x(), menu.y() - menu.height())
            if menu_rect.right() > desktop.right():
                menu.move(menu.x() - menu.width(), menu.y())
