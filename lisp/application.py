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

import json
from os.path import exists

from PyQt5.QtWidgets import QDialog, qApp

from lisp import layouts
from lisp import modules
from lisp import plugins
from lisp.core import configuration as cfg
from lisp.core.actions_handler import MainActionsHandler
from lisp.core.memento_model import AdapterMementoModel
from lisp.core.singleton import Singleton
from lisp.cues.cue_factory import CueFactory
from lisp.cues.cue_model import CueModel
from lisp.ui import elogging
from lisp.ui.layoutselect import LayoutSelect
from lisp.ui.mainwindow import MainWindow
from lisp.ui.settings.app_settings import AppSettings
from lisp.ui.settings.pages.app_general import AppGeneral
from lisp.ui.settings.pages.cue_app_settings import CueAppSettings


class Application(metaclass=Singleton):
    def __init__(self):
        self._mainWindow = MainWindow()
        self._app_conf = {}
        self._layout = None
        self._memento_model = None
        self._cue_model = CueModel()

        # Connect mainWindow actions
        self._mainWindow.new_session.connect(self.new_session_dialog)
        self._mainWindow.save_session.connect(self._save_to_file)
        self._mainWindow.open_session.connect(self._load_from_file)

        # Register general settings widget
        AppSettings.register_settings_widget(AppGeneral)
        AppSettings.register_settings_widget(CueAppSettings)

        # Show the mainWindow maximized
        self._mainWindow.showMaximized()

    @property
    def layout(self):
        """:rtype: lisp.layouts.cue_layout.CueLayout"""
        return self._layout

    @property
    def cue_model(self):
        """:rtype: lisp.cues.cue_model.CueModel"""
        return self._cue_model

    def start(self, session_file=''):
        if exists(session_file):
            self._load_from_file(session_file)
        elif cfg.config['Layout']['Default'].lower() != 'nodefault':
            layout = layouts.get_layout(cfg.config['Layout']['Default'])
            self._new_session(layout)
        else:
            self.new_session_dialog()

    def new_session_dialog(self):
        """Show the layout-selection dialog"""
        try:
            # Prompt the user for a new layout
            dialog = LayoutSelect()
            if dialog.exec_() != QDialog.Accepted:
                if self._layout is None:
                    # If the user close the dialog, and no layout exists
                    # the application is closed
                    self.finalize()
                    qApp.quit()
                    exit()
                else:
                    return

            # If a valid file is selected load it, otherwise load the layout
            if exists(dialog.filepath):
                self._load_from_file(dialog.filepath)
            else:
                self._new_session(dialog.selected())

        except Exception as e:
            elogging.exception('Startup error', e)
            qApp.quit()
            exit(-1)

    def _new_session(self, layout):
        self._delete_session()

        self._layout = layout(self._cue_model)
        self._memento_model = AdapterMementoModel(self.layout.model_adapter)
        self._mainWindow.set_layout(self._layout)
        self._app_conf['layout'] = layout.NAME

        plugins.init_plugins()

    def _delete_session(self):
        if self._layout is not None:
            MainActionsHandler.clear()
            plugins.reset_plugins()

            self._app_conf.clear()
            self._cue_model.reset()

            self._layout.finalize()
            self._layout = None
            self._memento_model = None
            self._cue_model.reset()

    def finalize(self):
        modules.terminate_modules()

        self._delete_session()
        self._mainWindow.deleteLater()

    def _save_to_file(self, session_file):
        """Save the current session into a file."""
        session = {"cues": [], "plugins": {}, "application": []}

        # Add the cues
        for cue in self._cue_model:
            session['cues'].append(cue.properties(only_changed=True))
        # Sort cues by index, allow sorted-models to load properly
        session['cues'].sort(key=lambda cue: cue['index'])

        session['plugins'] = plugins.get_plugin_settings()
        session['application'] = self._app_conf

        # Write to a file the json-encoded dictionary
        with open(session_file, mode='w', encoding='utf-8') as file:
            file.write(json.dumps(session, sort_keys=True, indent=4))

        MainActionsHandler.set_saved()
        self._mainWindow.update_window_title()

    def _load_from_file(self, session_file):
        """ Load a saved session from file """
        try:
            with open(session_file, mode='r', encoding='utf-8') as file:
                session = json.load(file)

            # New session
            self._new_session(
                layouts.get_layout(session['application']['layout']))
            # Get the application settings
            self._app_conf = session['application']

            # Load cues
            for cue_conf in session['cues']:
                cue_type = cue_conf.pop('_type_', 'Undefined')
                cue_id = cue_conf.pop('id')
                try:
                    cue = CueFactory.create_cue(cue_type, cue_id=cue_id)
                    cue.update_properties(cue_conf)
                    self._cue_model.add(cue)
                except Exception as e:
                    elogging.exception('Unable to create the cue', e)

            MainActionsHandler.set_saved()
            self._mainWindow.update_window_title()

            # Load plugins settings
            plugins.set_plugins_settings(session['plugins'])

            # Update the main-window
            self._mainWindow.filename = session_file
            self._mainWindow.update()
        except Exception as e:
            elogging.exception('Error during file reading', e)
            self.new_session_dialog()
