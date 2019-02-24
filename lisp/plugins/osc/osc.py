# This file is part of Linux Show Player
#
# Copyright 2019 Francesco Ceruti <ceppofrancy@gmail.com>
# Copyright 2016 Thomas Achtner <info@offtools.de>
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
from PyQt5.QtCore import QT_TRANSLATE_NOOP

from lisp.core.plugin import Plugin
from lisp.cues.cue_factory import CueFactory
from lisp.plugins.osc.osc_cue import OscCue
from lisp.plugins.osc.osc_server import OscServer
from lisp.plugins.osc.osc_settings import OscSettings
from lisp.ui.settings.app_configuration import AppConfigurationDialog


class Osc(Plugin):
    """Provide OSC I/O functionality"""

    Name = "OSC"
    Authors = ("Thomas Achtner",)
    Description = "Provide OSC I/O functionality"

    def __init__(self, app):
        super().__init__(app)

        # Register the settings widget
        AppConfigurationDialog.registerSettingsPage(
            "plugins.osc", OscSettings, Osc.Config
        )
        # Register the cue
        CueFactory.register_factory(OscCue.__name__, OscCue)
        app.window.registerSimpleCueMenu(
            OscCue, QT_TRANSLATE_NOOP("CueCategory", "Integration cues")
        )

        # Create a server instance
        self.__server = OscServer(
            Osc.Config["hostname"], Osc.Config["inPort"], Osc.Config["outPort"]
        )
        self.__server.start()

        Osc.Config.changed.connect(self.__config_change)
        Osc.Config.updated.connect(self.__config_update)

    @property
    def server(self):
        return self.__server

    def terminate(self):
        self.__server.stop()

    def __config_change(self, key, value):
        if key == "hostname":
            self.__server.hostname = value
        elif key == "inPort":
            self.__server.in_port = value
        elif key == "outPort":
            self.__server.out_port = value

    def __config_update(self, diff):
        for key, value in diff.items():
            self.__config_change(key, value)
