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

import json
import logging
from PyQt5.QtWidgets import QDialog, qApp
from os.path import exists, dirname

from lisp import layout
from lisp.core.actions_handler import MainActionsHandler
from lisp.core.session import Session
from lisp.core.signal import Signal
from lisp.core.singleton import Singleton
from lisp.core.util import filter_live_properties
from lisp.cues.cue import Cue
from lisp.cues.cue_factory import CueFactory
from lisp.cues.cue_model import CueModel
from lisp.cues.media_cue import MediaCue
from lisp.ui.layoutselect import LayoutSelect
from lisp.ui.mainwindow import MainWindow
from lisp.ui.settings.app_configuration import AppConfigurationDialog
from lisp.ui.settings.app_pages.cue import CueAppSettings
from lisp.ui.settings.app_pages.general import AppGeneral
from lisp.ui.settings.app_pages.layouts import LayoutsSettings
from lisp.ui.settings.app_pages.plugins import PluginsSettings
from lisp.ui.settings.cue_pages.cue_appearance import Appearance
from lisp.ui.settings.cue_pages.cue_general import CueGeneralSettingsPage
from lisp.ui.settings.cue_pages.media_cue import MediaCueSettings
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)


class Application(metaclass=Singleton):
    def __init__(self, app_conf):
        self.conf = app_conf

        self.session_created = Signal()
        self.session_before_finalize = Signal()

        self.__main_window = MainWindow(self.conf)
        self.__cue_model = CueModel()
        self.__session = None

        # Register general settings widget
        AppConfigurationDialog.registerSettingsPage(
            "general", AppGeneral, self.conf
        )
        AppConfigurationDialog.registerSettingsPage(
            "general.cue", CueAppSettings, self.conf
        )
        AppConfigurationDialog.registerSettingsPage(
            "layouts", LayoutsSettings, self.conf
        )
        AppConfigurationDialog.registerSettingsPage(
            "plugins", PluginsSettings, self.conf
        )

        # Register common cue-settings widgets
        CueSettingsRegistry().add(CueGeneralSettingsPage, Cue)
        CueSettingsRegistry().add(MediaCueSettings, MediaCue)
        CueSettingsRegistry().add(Appearance)

        # Connect mainWindow actions
        self.__main_window.new_session.connect(self._new_session_dialog)
        self.__main_window.save_session.connect(self._save_to_file)
        self.__main_window.open_session.connect(self._load_from_file)

    @property
    def session(self):
        """:rtype: lisp.core.session.Session"""
        return self.__session

    @property
    def window(self):
        """:rtype: lisp.ui.mainwindow.MainWindow"""
        return self.__main_window

    @property
    def layout(self):
        """:rtype: lisp.layout.cue_layout.CueLayout"""
        return self.session.layout

    @property
    def cue_model(self):
        """:rtype: lisp.cues.cue_model.CueModel"""
        return self.__cue_model

    def start(self, session_file=""):
        # Show the mainWindow maximized
        self.__main_window.showMaximized()

        if exists(session_file):
            self._load_from_file(session_file)
        else:
            layout_name = self.conf.get("layout.default", "nodefault")

            if layout_name.lower() != "nodefault":
                self._new_session(layout.get_layout(layout_name))
            else:
                self._new_session_dialog()

    def finalize(self):
        self._delete_session()

        self.__cue_model = None
        self.__main_window = None

    def _new_session_dialog(self):
        """Show the layout-selection dialog"""
        try:
            # Prompt the user for a new layout
            dialog = LayoutSelect(self, parent=self.window)
            if dialog.exec() == QDialog.Accepted:
                # If a file is selected load it, otherwise load the layout
                if dialog.sessionPath:
                    self._load_from_file(dialog.sessionPath)
                else:
                    self._new_session(dialog.selected())
            else:
                if self.__session is None:
                    # If the user close the dialog, and no layout exists
                    # the application is closed
                    qApp.quit()
        except Exception:
            logger.critical(
                translate("ApplicationError", "Startup error"), exc_info=True
            )
            qApp.quit()

    def _new_session(self, layout):
        self._delete_session()

        self.__session = Session(layout(application=self))
        self.__main_window.setSession(self.__session)

        self.session_created.emit(self.__session)

    def _delete_session(self):
        if self.__session is not None:
            MainActionsHandler.clear()

            self.session_before_finalize.emit(self.session)

            self.__session.finalize()
            self.__session = None

    def _save_to_file(self, session_file):
        """Save the current session into a file."""
        self.session.session_file = session_file

        # Save session path
        self.conf.set("session.last_dir", dirname(session_file))
        self.conf.write()

        # Add the cues
        session_dict = {"cues": []}

        for cue in self.__cue_model:
            session_dict["cues"].append(
                cue.properties(defaults=False, filter=filter_live_properties)
            )
        # Sort cues by index, allow sorted-models to load properly
        session_dict["cues"].sort(key=lambda cue: cue["index"])

        # Get session settings
        session_dict["session"] = self.__session.properties()
        # Remove the 'session_file' property (not needed in the session file)
        session_dict["session"].pop("session_file", None)

        # Write to a file the json-encoded dictionary
        with open(session_file, mode="w", encoding="utf-8") as file:
            if self.conf["session.minSave"]:
                file.write(json.dumps(session_dict, separators=(",", ":")))
            else:
                file.write(json.dumps(session_dict, sort_keys=True, indent=4))

        MainActionsHandler.set_saved()
        self.__main_window.updateWindowTitle()

    def _load_from_file(self, session_file):
        """ Load a saved session from file """
        try:
            with open(session_file, mode="r", encoding="utf-8") as file:
                session_dict = json.load(file)

            # New session
            self._new_session(
                layout.get_layout(session_dict["session"]["layout_type"])
            )
            self.__session.update_properties(session_dict["session"])
            self.__session.session_file = session_file

            # Load cues
            for cues_dict in session_dict.get("cues", {}):
                cue_type = cues_dict.pop("_type_", "Undefined")
                cue_id = cues_dict.pop("id")
                try:
                    cue = CueFactory.create_cue(cue_type, cue_id=cue_id)
                    cue.update_properties(cues_dict)
                    self.__cue_model.add(cue)
                except Exception:
                    name = cues_dict.get("name", "No name")
                    logger.exception(
                        translate(
                            "ApplicationError",
                            'Unable to create the cue "{}"'.format(name),
                        )
                    )

            MainActionsHandler.set_saved()
            self.__main_window.updateWindowTitle()
        except Exception:
            logger.exception(
                translate(
                    "ApplicationError",
                    'Error while reading the session file "{}"',
                ).format(session_file)
            )
            self._new_session_dialog()
