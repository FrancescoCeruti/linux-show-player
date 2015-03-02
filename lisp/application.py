##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

import json
from os.path import exists
import sys
import traceback

from PyQt5.QtWidgets import QDialog, QMessageBox, qApp
from lisp import layouts
from lisp import modules
from lisp import plugins
from lisp.ui.layoutselect import LayoutSelect
from lisp.ui.mainwindow import MainWindow
from lisp.utils import configuration as cfg

from lisp.core.actions_handler import ActionsHandler
from lisp.cues.cue_factory import CueFactory
from lisp.ui.qmessagebox import QDetailedMessageBox
from lisp.ui.settings.app_settings import AppSettings
from lisp.ui.settings.sections.app_general import General
from lisp.core.singleton import Singleton


class Application(metaclass=Singleton):

    def __init__(self):
        # Create the mainWindow
        self.mainWindow = MainWindow()
        # Create a layout 'reference' and set to None
        self.layout = None
        # Create an empty configuration
        self.app_conf = {}

        # Initialize modules
        failed = modules.init_modules()
        for err in failed:
            msg = 'Module "' + err[0] + '" loading failed'
            QDetailedMessageBox.dcritical('Module error', msg, str(err[1]))

        # Connect mainWindow actions
        self.mainWindow.new_session.connect(self._startup)
        self.mainWindow.save_session.connect(self._save_to_file)
        self.mainWindow.open_session.connect(self._load_from_file)

        # Register general settings widget
        AppSettings.register_settings_widget(General)

        # Show the mainWindow maximized
        self.mainWindow.showMaximized()

    def start(self, filepath=''):
        if exists(filepath):
            # Load the file
            self.mainWindow.file = filepath
            self._load_from_file(filepath)
        else:
            # Create the layout
            self._startup(first=True)

    def finalize(self):
        self.layout.destroy_layout()

        # Terminate the loaded modules
        modules.terminate_modules()

    def _create_layout(self, layout):
        '''
            Clear ActionHandler session;
            Reset plugins;
            Creates a new layout;
            Init plugins.
        '''

        ActionsHandler().clear()
        plugins.reset_plugins()

        if self.layout is not None:
            self.layout.destroy_layout()
            self.layout = None

        try:
            self.layout = layout(self)
            self.mainWindow.set_layout(self.layout)
            self.app_conf['layout'] = layout.NAME
            self._init_plugins()
        except Exception:
            QMessageBox.critical(None, 'Error', 'Layout init failed')
            print(traceback.format_exc(), file=sys.stderr)

    def _layout_dialog(self):
        ''' Show the layout-selection dialog '''
        try:
            select = LayoutSelect()
            select.exec_()
        except Exception as e:
            QMessageBox.critical(None, 'Fatal error', str(e))
            qApp.quit()
            exit(-1)

        if select.result() != QDialog.Accepted:
            qApp.quit()
            exit()

        if exists(select.filepath):
            self._load_from_file(select.filepath)
        else:
            self._create_layout(select.slected())

    def _startup(self, first=False):
        ''' Initializes the basic components '''
        self.mainWindow.file = ''
        self.app_conf = {}

        if first and cfg.config['Layout']['Default'].lower() != 'nodefault':
            layout = layouts.get_layout(cfg.config['Layout']['Default'])
            self._create_layout(layout)
        else:
            self._layout_dialog()

    def _save_to_file(self, filepath):
        ''' Save the current program into "filepath" '''

        # Empty structure
        program = {"cues": [], "plugins": {}, "application": []}

        # Add the cues
        for cue in self.layout.get_cues():
            if cue is not None:
                program['cues'].append(cue.properties())

        # Add the plugins
        failed = program['plugins'] = plugins.get_plugin_settings()
        for err in failed:
            msg = 'Plugin "' + err[0] + '" saving failed'
            QDetailedMessageBox.dcritical('Plugin error', msg, str(err[1]))

        # Add the app settings
        program['application'] = self.app_conf

        # Write to a file the json-encoded dictionary
        with open(filepath, mode='w', encoding='utf-8') as file:
            file.write(json.dumps(program, sort_keys=True, indent=4))

        ActionsHandler().set_saved()
        self.mainWindow.update_window_title()

    def _load_from_file(self, filepath):
        ''' Loads a saved program from "filepath" '''
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
                cue = CueFactory.create_cue(cue_conf)
                if cue is not None:
                    self.layout.add_cue(cue, cue['index'])

            ActionsHandler().set_saved()
            self.mainWindow.update_window_title()

            # Load plugins settings
            self._load_plugins_settings(program['plugins'])

            # Update the main-window
            self.mainWindow.file = filepath
            self.mainWindow.update()
        except Exception:
            QMessageBox.critical(None, 'Error', 'Error during file reading')
            print(traceback.format_exc(), file=sys.stderr)

            self._startup()

    def _init_plugins(self):
        ''' Initialize all the plugins '''
        failed = plugins.init_plugins()

        for err in failed:
            msg = 'Plugin "' + err[0] + '" initialization failed'
            QDetailedMessageBox.dcritical('Plugin error', msg, str(err[1]))

    def _load_plugins_settings(self, settings):
        ''' Loads all the plugins settings '''

        failed = plugins.set_plugins_settings(settings)

        for err in failed:
            msg = 'Plugin "' + err[0] + '" loading failed'
            QDetailedMessageBox.dcritical('Plugin error', msg, str(err[1]))
