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

from lisp.core.plugin import Plugin

from lisp.application import Application
from lisp.cues.media_cue import MediaCue
from lisp.plugins.triggers.triggers_handler import TriggersHandler
from lisp.plugins.triggers.triggers_settings import TriggersSettings


class Triggers(Plugin):

    def __init__(self):
        super().__init__()

        self.app = Application()
        self.handlers = {}

        self.app.layout.cue_added.connect(self.on_cue_added)
        self.app.layout.cue_removed.connect(self.on_cue_removed)
        self.app.layout.add_settings_section(TriggersSettings,
                                             cue_class=MediaCue)

    def reset(self):
        self.app.layout.cue_added.disconnect(self.on_cue_added)
        self.app.layout.cue_removed.disconnect(self.on_cue_removed)
        self.app.layout.remove_settings_section(TriggersSettings)

        for handler in self.handlers.values():
            handler.finalize()

        self.handlers.clear()

    def on_cue_added(self, cue):
        if isinstance(cue, MediaCue):
            self.update_handler(cue)
            cue.updated.connect(self.update_handler)

    def on_cue_removed(self, cue):
        if isinstance(cue, MediaCue):
            self.handlers.pop(cue, None)
            cue.updated.disconnect(self.update_handler)

    def update_handler(self, cue):
        if 'triggers' in cue.properties():
            if len(cue['triggers']) > 0:
                if cue not in self.handlers:
                    self.handlers[cue] = TriggersHandler(cue.media)
                self.handlers[cue].reset_triggers()
                self.handlers[cue].load_triggers(cue['triggers'])
            else:
                self.handlers.pop(cue, None)
