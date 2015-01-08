##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

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
                self._ensure_int_keys(cue['triggers'])
                if cue not in self.handlers:
                    self.handlers[cue] = TriggersHandler(cue.media)
                self.handlers[cue].reset_triggers()
                self.handlers[cue].load_triggers(cue['triggers'])
            else:
                self.handlers.pop(cue, None)

    def _ensure_int_keys(self, triggers):
        for key in triggers:
            if isinstance(key, str):
                value = triggers.pop(key)
                triggers[int(key)] = value
