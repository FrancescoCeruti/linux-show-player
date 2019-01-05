# This file is part of Linux Show Player
#
# Copyright 2018 Francesco Ceruti <ceppofrancy@gmail.com>
# Copyright 2016-2017 Thomas Achtner <info@offtools.de>
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

import logging

from lisp.core.properties import Property
from lisp.core.plugin import Plugin
from lisp.core.signal import Connection
from lisp.cues.cue import Cue
from lisp.cues.media_cue import MediaCue
from lisp.plugins.timecode import protocols
from lisp.plugins.timecode.cue_tracker import TimecodeCueTracker, TcFormat
from lisp.plugins.timecode.protocol import TimecodeProtocol
from lisp.plugins.timecode.settings import TimecodeAppSettings, TimecodeSettings
from lisp.ui.settings.app_configuration import AppConfigurationDialog
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)


class Timecode(Plugin):
    Name = "Timecode"
    Authors = ("Thomas Achtner",)
    OptDepends = ("Midi",)
    Description = "Provide timecode via multiple protocols"

    def __init__(self, app):
        super().__init__(app)

        # Register a new Cue property to store settings
        Cue.timecode = Property(
            default={"enabled": False, "replace_hours": False, "track": 0}
        )

        # Register cue-settings-page
        CueSettingsRegistry().add(TimecodeSettings, MediaCue)
        # Register the settings widget
        AppConfigurationDialog.registerSettingsPage(
            "plugins.timecode", TimecodeAppSettings, Timecode.Config
        )

        # Load available protocols
        protocols.load_protocols()

        # Create the cue tracker object
        self.__cue_tracker = TimecodeCueTracker(
            self.__get_protocol(Timecode.Config["protocol"]),
            TcFormat[Timecode.Config["format"]],
        )

        # Cues with timecode-tracking enabled
        self.__cues = set()

        # Watch for session finalization(s)
        self.app.session_before_finalize.connect(self.__session_finalize)

        # Watch cue-model changes
        self.app.cue_model.item_added.connect(self.__cue_added)
        self.app.cue_model.item_removed.connect(self.__cue_removed)

        Timecode.Config.changed.connect(self.__config_change)
        Timecode.Config.updated.connect(self.__config_update)

    def finalize(self):
        self.__cue_tracker.finalize()

    def __config_change(self, key, value):
        if key == "protocol":
            self.__cue_tracker.protocol = self.__get_protocol(value)
        elif key == "format":
            self.__cue_tracker.format = value

    def __config_update(self, diff):
        for key, value in diff.items():
            self.__config_change(key, value)

    def __get_protocol(self, protocol_name):
        try:
            return protocols.get_protocol(protocol_name)()
        except Exception:
            logger.error(
                translate(
                    "Timecode", 'Cannot load timecode protocol: "{}"'
                ).format(protocol_name),
                exc_info=True,
            )
            # Use a dummy protocol in case of failure
            return TimecodeProtocol()

    def __session_finalize(self):
        self.__cue_tracker.untrack()
        self.__cues.clear()

    def __cue_changed(self, cue, property_name, value):
        if property_name == "timecode":
            if value.get("enabled", False):
                cue.started.connect(
                    self.__cue_tracker.track, Connection.QtQueued
                )
            else:
                self.__disable_on_cue(cue)

    def __cue_added(self, cue):
        cue.property_changed.connect(self.__cue_changed)
        # Check for current cue settings
        self.__cue_changed(cue, "timecode", cue.timecode)

    def __cue_removed(self, cue):
        cue.property_changed.disconnect(self.__cue_changed)
        self.__disable_on_cue(cue)

    def __disable_on_cue(self, cue):
        # If it's not connected this does nothing
        cue.started.disconnect(self.__cue_tracker.track)

        # If the cue is tracked, stop the tracking
        if self.__cue_tracker.cue is cue:
            self.__cue_tracker.untrack()
