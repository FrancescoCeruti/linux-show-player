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

from lisp.application import Application
from lisp.core.plugin import Plugin
from lisp.plugins.triggers.triggers_handler import CueHandler
from lisp.plugins.triggers.triggers_settings import TriggersSettings
from lisp.ui.settings.cue_settings import CueSettingsRegistry


class Triggers(Plugin):

    Name = 'Triggers'

    def __init__(self):
        super().__init__()

        TriggersSettings.PluginInstance = self
        CueSettingsRegistry().add_item(TriggersSettings)
        Application().cue_model.item_added.connect(self._cue_added)
        Application().cue_model.item_added.connect(self._cue_removed)

        self.triggers = {}
        self.handlers = {}

    def update_handler(self, cue, triggers):
        self.triggers[cue.id] = triggers

        if cue in self.handlers:
            self.handlers[cue.id].triggers = triggers
        else:
            self._cue_added(cue)

    def load_settings(self, settings):
        self.triggers = settings

        for cue_id in self.triggers:
            cue = Application().cue_model.get(cue_id)
            if cue is not None:
                self._cue_added(cue)

    def settings(self):
        settings = {}

        for cue_id, cue_triggers in self.triggers.items():
            if Application().cue_model.get(cue_id) is not None:
                settings[cue_id] = cue_triggers

        return settings

    def reset(self):
        for handler in self.handlers.values():
            handler.finalize()

        self.handlers.clear()
        self.triggers.clear()

    def _cue_added(self, cue):
        if cue.id in self.triggers:
            self.handlers[cue.id] = CueHandler(cue, self.triggers[cue.id])

    def _cue_removed(self, cue):
        handler = self.handlers.pop(cue.id, None)
        if handler is not None:
            handler.finalize()
