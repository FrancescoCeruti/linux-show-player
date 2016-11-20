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

from collections import namedtuple

from lisp.application import Application, AppSettings
from lisp.core.has_properties import Property
from lisp.core.plugin import Plugin
from lisp.cues.cue import Cue
from lisp.cues.media_cue import MediaCue
from lisp.cues.cue_time import CueTime
from lisp.plugins.timecode.timecode_settings import TimecodeCueSettings,\
    TimecodeSettings
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.utils.util import time_tuple
from lisp.utils.configuration import config
from lisp.utils import elogging

from ola.OlaClient import OLADNotRunningException, OlaClient

TimecodeFormatDef = namedtuple('TimecodeDef', ['format', 'millis'])


class OlaTimecode():
    __TC_DEF__ = {
        'FILM'  : TimecodeFormatDef(format=OlaClient.TIMECODE_FILM, millis=1000/24),
        'EBU'   : TimecodeFormatDef(format=OlaClient.TIMECODE_EBU, millis=1000/25),
        'SMPTE' : TimecodeFormatDef(format=OlaClient.TIMECODE_SMPTE, millis=1000/30)
    }

    def __init__(self):
        try:
            self.__client = OlaClient()
        except OLADNotRunningException:
            self.__client = None
        self.__handler = None
        self.__format = self.__TC_DEF__[config['Timecode']['format']].format
        self.__millis = self.__TC_DEF__[config['Timecode']['format']].millis
        self.__use_hours = False
        self.__track = 0

    def status(self):
        return bool(self.__client)

    def __send_timecode(self, time):
        tt = time_tuple(time)
        try:
            if self.__use_hours:
                self.__client.SendTimeCode(self.__format, self.__track, tt[1], tt[2], round(tt[3] / self.__millis), 0)
            else:
                self.__client.SendTimeCode(self.__format, tt[0], tt[1], tt[2], round(tt[3] / self.__millis), 0)
        except OLADNotRunningException:
            self.stop_timecode()
            config.set('Timecode', 'enabled', 'False')
            elogging.warning('Plugin Timecode disabled', details='Ola is not running', dialog=False)

    def start_timecode(self, handler):
        # get current timecode format settings
        self.__format = self.__TC_DEF__[config['Timecode']['format']].format
        self.__millis = self.__TC_DEF__[config['Timecode']['format']].millis

        # disconnect old handler
        self.stop_timecode()

        # test plugin enabled
        if config['Timecode']['enabled'] is False:
            return

        # timecode for handler enabled
        if handler.enabled:
            self.__handler = handler
            self.__use_hours = self.__handler.use_hours
            self.__track = self.__handler.track
        else:
            return

        # test and create client, return on False
        if not self.__client:
            try:
                self.__client = OlaClient()
            except OLADNotRunningException:
                return

        self.__handler.notify.connect(self.__send_timecode)

    def stop_timecode(self):
        if self.__handler:
            self.__handler.notify.disconnect()


class TimecodeHandler(CueTime):
    def __init__(self, cue):
        super().__init__(cue)

        self.__cue = cue
        self.__conf = cue.timecode

    @property
    def enabled(self):
        if 'enabled' in self.__conf:
            return self.__conf['enabled']
        else:
            return False

    @property
    def use_hours(self):
        if 'use_hours' in self.__conf:
            return self.__conf['use_hours']
        else:
            return False

    @property
    def track(self):
        if 'track' in self.__conf:
            return self.__conf['track']
        else:
            return 0

    def update_conf(self, timecode):
        self.__conf = timecode


class Timecode(Plugin):

    Name = "Timecode"
    
    def __init__(self):
        super().__init__()

        self.__handlers = {}

        # Register a new Cue property to store settings
        Cue.register_property('timecode', Property(default={}))

        # Register cue-settings-page
        CueSettingsRegistry().add_item(TimecodeCueSettings, MediaCue)

        # Register pref-settings-page
        AppSettings.register_settings_widget(TimecodeSettings)

        # Connect Timecode
        Application().cue_model.item_added.connect(self.__cue_added)
        Application().cue_model.item_removed.connect(self.__cue_removed)

        self.__client = OlaTimecode()

    def init(self):
        if not self.__client.status() and config['Timecode']['enabled']:
            config.set('Timecode', 'enabled', 'False')
            elogging.warning('Plugin Timecode disabled', details='Ola is not running', dialog=False)

    def __cue_changed(self, cue, property_name, value):
        if property_name == 'timecode':
            if cue.id in self.__handlers:
                self.__handlers[cue.id].update_conf(cue.timecode)
            else:
                self.__handlers[cue.id] = TimecodeHandler(cue)
                cue.started.connect(self.__cue_started)

    def __cue_added(self, cue):
        cue.property_changed.connect(self.__cue_changed)
        self.__cue_changed(cue, 'timecode', cue.timecode)

    def __cue_removed(self, cue):
        cue.property_changed.disconnect(self.__cue_changed)
        self.__client.stop_timecode()
        self.__handlers.pop(cue.id, None)

    def __cue_started(self, cue):
        self.__client.start_timecode(self.__handlers[cue.id])