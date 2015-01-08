##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from abc import abstractmethod

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import *  # @UnusedWildImport
from lisp.ui.mainwindow import MainWindow

from lisp.actions.actions_handler import ActionsHandler
from lisp.cues.cue import Cue
from lisp.layouts.cue_layout_actions import AddAction, ConfigureAction, \
    MultiConfigureAction, MoveAction, RemoveAction
from lisp.ui.settings.cue_settings import CueSettings
from lisp.ui.settings.section import SettingsSection


class CueLayout(QObject):

    # Layout name
    NAME = 'Base'
    # Layout description (html)
    DESCRIPTION = '<p>No description</p>'

    # Media added to the layout
    cue_added = pyqtSignal(Cue)
    # Media removed from the layout
    cue_removed = pyqtSignal(Cue)
    # Media focused
    focus_changed = pyqtSignal(Cue)
    # A key is pressed
    key_pressed = pyqtSignal(object)

    _settings_sections = {}
    _context_items = {}

    def __init__(self, **kwds):
        super().__init__(**kwds)

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

    def add_cue(self, cue, index=None):
        action = AddAction(self, cue, index)
        ActionsHandler().do_action(action)

    def add_cues(self, cues):
        for cue in filter(lambda c: c is not None, cues):
            self.add_cue(cue)

    @abstractmethod
    def __add_cue__(self, cue, index=None):
        '''Add the cue to the layout'''

    @classmethod
    def add_settings_section(cls, section, cue_class=Cue):
        if issubclass(section, SettingsSection):
            if cue_class not in cls._settings_sections:
                cls._settings_sections[cue_class] = [section]
            elif section not in cls._settings_sections[cue_class]:
                cls._settings_sections[cue_class].append(section)

    @abstractmethod
    def clear_layout(self):
        '''Reset the layout elements'''

    @abstractmethod
    def deselect_all(self):
        '''Deselect all the cues'''

    @abstractmethod
    def destroy_layout(self):
        '''Destroy all the layout elements'''

    def edit_cue(self, cue):
        widgets = []
        for cue_class in self._settings_sections:
            if issubclass(cue.__class__, cue_class):
                widgets.extend(self._settings_sections[cue_class])

        if len(widgets) > 0:
            widgets.sort(key=lambda w: w.Name)

            edit_ui = CueSettings(widgets, cue, parent=MainWindow())

            def on_apply(settings):
                action = ConfigureAction(settings, cue)
                ActionsHandler().do_action(action)

            edit_ui.on_apply.connect(on_apply)
            edit_ui.exec_()

    def edit_selected_cues(self):
        cues = self.get_selected_cues()

        if len(cues) > 0:
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
                ActionsHandler().do_action(action)

            edit_ui.on_apply.connect(on_apply)
            edit_ui.exec_()

    @abstractmethod
    def get_context_cue(self):
        '''Return the last cue in the context-menu scope, or None'''
        return None

    @abstractmethod
    def get_cue_at(self, index):
        '''Return the cue at the given index, or None'''
        return None

    @abstractmethod
    def get_cue_by_id(self, cue_id):
        '''Return the cue with the given id, or None'''
        return None

    @abstractmethod
    def get_cues(self, cue_class=Cue):
        '''Get all the cues as 1d-list'''
        return []

    @abstractmethod
    def get_selected_cues(self, cue_class=Cue):
        '''Return an "ordered" list of all selected cues'''
        return []

    @abstractmethod
    def invert_selection(self):
        '''Invert selection'''

    def move_cue(self, cue, index):
        action = MoveAction(self, cue, index)
        ActionsHandler().do_action(action)

    @abstractmethod
    def __move_cue__(self, cue, index):
        '''Move the given cue at the given index'''

    def remove_cue(self, cue):
        action = RemoveAction(self, cue, cue['index'])
        ActionsHandler().do_action(action)

    def remove_cue_at(self, index):
        action = RemoveAction(self, self.get_cue_at(index), index)
        ActionsHandler().do_action(action)

    @abstractmethod
    def __remove_cue__(self, cue):
        '''Remove the given cue'''

    @classmethod
    def remove_context_item(cls, item):
        for key in cls._context_items:
            cls._context_items[key] = [i for i in cls._context_items[key]
                                       if i != item]

    @classmethod
    def remove_settings_section(cls, section):
        for key in cls._settings_sections:
            cls._settings_sections[key] = [s for s in
                                           cls._settings_sections[key]
                                           if s != section]

    '''
    @classmethod
    def reset_context_items(cls, cue_class=Cue):
        for cclass in list(cls._context_items):
            if issubclass(cclass, cue_class):
                cls._context_items.pop(cclass, None)

    @classmethod
    def reset_settings_sections(cls, cue_class=Cue):
        for cclass in list(cls._settings_sections):
            if issubclass(cclass, cue_class):
                cls._settings_sections.pop(cclass, None)
    '''

    @abstractmethod
    def select_all(self):
        '''Select all the cues'''

    def show_context_menu(self, position):
        items = []
        for class_ in sorted(self._context_items.keys(), key=lambda i: str(i)):
            if isinstance(self.get_context_cue(), class_):
                items.extend(self._context_items[class_])

        if len(items) > 0:
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
