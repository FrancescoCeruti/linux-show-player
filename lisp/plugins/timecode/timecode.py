# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
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


from lisp.application import Application
from lisp.core.has_properties import Property
from lisp.core.plugin import Plugin
from lisp.core.signal import Connection
from lisp.cues.cue import Cue
from lisp.cues.media_cue import MediaCue
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.settings.app_settings import AppSettings
from lisp.plugins.timecode.timecode_common import TimecodeCommon
from lisp.plugins.timecode.timecode_settings import TimecodeAppSettings, TimecodeSettings


class Timecode(Plugin):
    Name = 'Timecode'

    def __init__(self):
        super().__init__()
        self.__cues = set()

        # Register a new Cue property to store settings
        Cue.register_property('timecode', Property(default={}))

        # Register cue-settings-page
        CueSettingsRegistry().add_item(TimecodeSettings, MediaCue)

        # Register the settings widget
        AppSettings.register_settings_widget(TimecodeAppSettings)

        # Watch cue-model changes
        Application().cue_model.item_added.connect(self.__cue_added)
        Application().cue_model.item_removed.connect(self.__cue_removed)

    def init(self):
        TimecodeCommon().init()

    def reset(self):
        self.__cues.clear()
        TimecodeCommon().stop(rclient=True, rcue=True)

    def __cue_changed(self, cue, property_name, value):
        if property_name == 'timecode':
            if value.get('enabled', False):
                if cue.id not in self.__cues:
                    self.__cues.add(cue.id)
                    cue.started.connect(self.__cue_started, Connection.QtQueued)
            else:
                self.__cue_removed(cue)

    def __cue_added(self, cue):
        cue.property_changed.connect(self.__cue_changed)
        self.__cue_changed(cue, 'timecode', cue.timecode)

    def __cue_removed(self, cue):
        try:
            self.__cues.remove(cue.id)
            if TimecodeCommon().cue is cue:
                TimecodeCommon().stop(rcue=True)
            cue.started.disconnect(self.__cue_started)
            cue.property_changed.disconnect(self.__cue_changed)
        except KeyError:
            pass

    def __cue_started(self, cue):
            TimecodeCommon().start(cue)
