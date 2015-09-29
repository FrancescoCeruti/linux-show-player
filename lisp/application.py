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

import json
from os.path import exists
import traceback

from PyQt5.QtWidgets import QDialog, qApp

from lisp import layouts
from lisp import modules
from lisp import plugins
from lisp.ui.layoutselect import LayoutSelect
from lisp.ui.mainwindow import MainWindow
from lisp.utils import configuration as cfg
from lisp.utils import logging
from lisp.core.actions_handler import ActionsHandler
from lisp.core.singleton import Singleton
from lisp.cues.cue_factory import CueFactory
from lisp.ui.settings.app_settings import AppSettings
from lisp.ui.settings.sections.app_general import General


class Application(metaclass=Singleton):
    def __init__(self):
        # Create the mainWindow
        self.mainWindow = MainWindow()
        # Create a layout 'reference' and set to None
        self._layout = None
        # Create an empty configuration
        self.app_conf = {}

        # Initialize modules
        modules.init_modules()

        # Connect mainWindow actions
        self.mainWindow.new_session.connect(self._startup)
        self.mainWindow.save_session.connect(self._save_to_file)
        self.mainWindow.open_session.connect(self._load_from_file)

        # Register general settings widget
        AppSettings.register_settings_widget(General)

        # Show the mainWindow maximized
        self.mainWindow.showMaximized()

    @property
    def layout(self):
        """:rtype: lisp.layouts.cue_layout.CueLayout"""
        return self._layout

    def start(self, filepath=''):
        if exists(filepath):
            # Load the file
            self.mainWindow.file = filepath
            self._load_from_file(filepath)
        else:
            # Create the layout
            self._startup(first=True)

    def finalize(self):
        self._layout.destroy_layout()

        # Terminate the loaded modules
        modules.terminate_modules()

    def _create_layout(self, layout):
        """
            Clear ActionHandler session;
            Reset plugins;
            Creates a new layout;
            Init plugins.
        """

        ActionsHandler().clear()
        plugins.reset_plugins()

        if self._layout is not None:
            self._layout.destroy_layout()
            self._layout = None

        try:
            self._layout = layout(self)
            self.mainWindow.set_layout(self._layout)
            self.app_conf['layout'] = layout.NAME
            self._init_plugins()
        except Exception:
            logging.error('Layout init failed', details=traceback.format_exc())

    def _layout_dialog(self):
        """ Show the layout-selection dialog """
        try:
            select = LayoutSelect()
            select.exec_()

            if select.result() != QDialog.Accepted:
                qApp.quit()
                exit()

            if exists(select.filepath):
                self._load_from_file(select.filepath)
            else:
                self._create_layout(select.slected())

        except Exception:
            logging.error('Startup error', details=traceback.format_exc())
            qApp.quit()
            exit(-1)

    def _startup(self, first=False):
        """ Initialize the basic components """
        self.mainWindow.file = ''
        self.app_conf = {}

        if first and cfg.config['Layout']['Default'].lower() != 'nodefault':
            layout = layouts.get_layout(cfg.config['Layout']['Default'])
            self._create_layout(layout)
        else:
            self._layout_dialog()

    def _save_to_file(self, filepath):
        """ Save the current program into "filepath" """

        # Empty structure
        program = {"cues": [], "plugins": {}, "application": []}

        # Add the cues
        for cue in self._layout.get_cues():
            if cue is not None:
                program['cues'].append(cue.properties())

        # Add the plugins
        program['plugins'] = plugins.get_plugin_settings()

        # Add the app settings
        program['application'] = self.app_conf

        # Write to a file the json-encoded dictionary
        with open(filepath, mode='w', encoding='utf-8') as file:
            file.write(json.dumps(program, sort_keys=True, indent=4))

        ActionsHandler().set_saved()
        self.mainWindow.update_window_title()

    def _load_from_file(self, filepath):
        """ Loads a saved program from "filepath" """
        try:
            # Read the file
            with open(filepath, mode='r', encoding='utf-8') as file:
                program = json.load(file)

            # Get the application settings
            self.app_conf = program['application']

            # Create the layout
            self._create_layout(layouts.get_layout(self.app_conf['layout']))

            # Load cues
            for cue_conf in program['cues']:
                cue_type = cue_conf.pop('_type_', 'Undefined')
                try:
                    cue = CueFactory.create_cue(cue_type)
                    cue.update_properties(cue_conf)
                    self._layout.add_cue(cue, cue.index)
                except Exception as e:
                    logging.exception('Unable to create the cue', e)

            ActionsHandler().set_saved()
            self.mainWindow.update_window_title()

            # Load plugins settings
            self._load_plugins_settings(program['plugins'])

            # Update the main-window
            self.mainWindow.file = filepath
            self.mainWindow.update()
        except Exception as e:
            logging.error('Error during file reading', e)

            self._startup()

    def _init_plugins(self):
        """ Initialize all the plugins """
        plugins.init_plugins()

    def _load_plugins_settings(self, settings):
        """ Loads all the plugins settings """
        plugins.set_plugins_settings(settings)
