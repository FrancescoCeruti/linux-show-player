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

from lisp.core.plugin import Plugin
from lisp.core.properties import Property
from lisp.cues.cue import Cue
from lisp.plugins.triggers.triggers_handler import CueHandler
from lisp.plugins.triggers.triggers_settings import TriggersSettings
from lisp.ui.settings.cue_settings import CueSettingsRegistry


class Triggers(Plugin):

    Name = "Triggers"
    Authors = ("Francesco Ceruti",)
    Description = "Allow cues to react to other-cues state changes"

    def __init__(self, app):
        super().__init__(app)

        self.__handlers = {}

        # Register a Cue property to store settings
        Cue.triggers = Property({})
        # Cue.triggers -> {trigger: [(target_id, action), ...]}

        # Register SettingsPage
        CueSettingsRegistry().add(TriggersSettings)

        # On session destroy
        self.app.session_before_finalize.connect(self.session_reset)

        self.app.cue_model.item_added.connect(self.__cue_added)
        self.app.cue_model.item_removed.connect(self.__cue_removed)

    def session_reset(self):
        self.__handlers.clear()

    def __cue_changed(self, cue, property_name, value):
        if property_name == "triggers":
            if cue.id in self.__handlers:
                self.__handlers[cue.id].triggers = cue.triggers
            else:
                self.__handlers[cue.id] = CueHandler(
                    self.app, cue, cue.triggers
                )

    def __cue_added(self, cue):
        cue.property_changed.connect(self.__cue_changed)
        self.__cue_changed(cue, "triggers", cue.triggers)

    def __cue_removed(self, cue):
        cue.property_changed.disconnect(self.__cue_changed)
        self.__handlers.pop(cue.id, None)
