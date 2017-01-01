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

import logging
from collections import namedtuple

from ola.OlaClient import OLADNotRunningException, OlaClient

from lisp.application import Application
from lisp.core.clock import Clock
from lisp.core.configuration import config
from lisp.core.has_properties import Property
from lisp.core.plugin import Plugin
from lisp.core.signal import Connection
from lisp.core.util import time_tuple
from lisp.cues.cue import Cue
from lisp.cues.cue_time import CueTime
from lisp.cues.media_cue import MediaCue
from lisp.plugins.timecode.timecode_settings import TimecodeCueSettings, \
    TimecodeSettings
from lisp.ui import elogging
from lisp.ui.settings.app_settings import AppSettings
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.ui_utils import translate

TcFormatDef = namedtuple('TimecodeDef', ['format', 'millis'])
TcFormat = {
    'FILM': TcFormatDef(format=OlaClient.TIMECODE_FILM, millis=1000 / 24),
    'EBU': TcFormatDef(format=OlaClient.TIMECODE_EBU, millis=1000 / 25),
    'SMPTE': TcFormatDef(format=OlaClient.TIMECODE_SMPTE, millis=1000 / 30)
}


class HRCueTime(CueTime):
    _Clock = Clock(30)  # 1000 /30  = 33.3333 milliseconds


class OlaTimecode:
    def __init__(self):
        try:
            self.__client = OlaClient()
        except OLADNotRunningException:
            self.__client = None

        self.__cue = None
        self.__cue_time = None

        self.__track = 0
        self.__hres = config['Timecode'].getboolean('hres')
        self.__format = TcFormat[config['Timecode']['format']].format
        self.__millis = TcFormat[config['Timecode']['format']].millis
        self.__replace_hours = False
        self.__last_frame = -1

    @property
    def cue(self):
        return self.__cue

    def status(self):
        return bool(self.__client)

    def start_timecode(self, cue):
        """Start the timecode, using the given cue."""
        # Test and create client, if needed, return on fail
        if not self.__client:
            try:
                self.__client = OlaClient()
            except OLADNotRunningException:
                logging.debug('TIMECODE: Cannot track cue, OLA not running.')
                return

        # Load cue settings, if enabled, otherwise return
        if not cue.timecode['enabled']:
            return

        # Stop the currently "running" timecode
        self.stop_timecode()

        # Reload format settings
        self.__hres = config['Timecode'].getboolean('hres')
        self.__format = TcFormat[config['Timecode']['format']].format
        self.__millis = TcFormat[config['Timecode']['format']].millis

        # Setup new cue and options
        self.__cue = cue
        self.__cue_time = HRCueTime(cue) if self.__hres else CueTime(cue)
        self.__replace_hours = cue.timecode['replace_hours']
        self.__track = cue.timecode['track']

        # Start watching the new cue
        self.__cue_time.notify.connect(
            self.__send_timecode, Connection.QtQueued)

    def stop_timecode(self, rclient=False, rcue=False):
        """Stop the timecode

        :param rclient: Reset the client
        :param rcue: Reset the cues
        """
        if self.__cue_time is not None:
            self.__cue_time.notify.disconnect(self.__send_timecode)

        self.__last_frame = -1
        if rclient:
            self.__client = None
        if rcue:
            self.__cue = None
            self.__cue_time = None

    def __send_timecode(self, time):
        tt = time_tuple(time)
        frame = int(tt[3] / self.__millis)

        if self.__hres:
            if self.__last_frame == frame:
                return
            self.__last_frame = frame

        try:
            if not self.__replace_hours:
                track = tt[0]
            else:
                track = self.__track

            self.__client.SendTimeCode(self.__format,
                                       track, tt[1], tt[2], frame)
        except OLADNotRunningException:
            self.stop_timecode(rclient=True, rcue=True)
            elogging.error(
                translate('Timecode', 'Cannot send timecode.'),
                details=translate('Timecode', 'OLA has stopped.'))
        except Exception as e:
            self.stop_timecode(rclient=True, rcue=True)
            elogging.exception('Cannot send timecode.', e, dialog=False)


class Timecode(Plugin):
    Name = 'Timecode'

    def __init__(self):
        super().__init__()
        self.__client = OlaTimecode()
        self.__cues = set()

        # Register a new Cue property to store settings
        Cue.register_property('timecode', Property(default={}))

        # Register cue-settings-page
        CueSettingsRegistry().add_item(TimecodeCueSettings, MediaCue)
        # Register pref-settings-page
        AppSettings.register_settings_widget(TimecodeSettings)

        # Watch cue-model changes
        Application().cue_model.item_added.connect(self.__cue_added)
        Application().cue_model.item_removed.connect(self.__cue_removed)

    def init(self):
        if not config['Timecode'].getboolean('enabled'):
            logging.info('TIMECODE: disabled by application settings')
        elif not self.__client.status():
            logging.info('TIMECODE: disabled, OLA not running')

    def reset(self):
        self.__cues.clear()
        self.__client.stop_timecode(rclient=True, rcue=True)

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
            if self.__client.cue is cue:
                self.__client.stop_timecode(rcue=True)

            cue.started.disconnect(self.__cue_started)
            cue.property_changed.disconnect(self.__cue_changed)
        except KeyError:
            pass

    def __cue_started(self, cue):
        if config['Timecode'].getboolean('enabled'):
            if cue is not self.__client.cue:
                self.__client.start_timecode(cue)
        elif cue is self.__client.cue:
            self.__client.stop_timecode(rcue=True)
