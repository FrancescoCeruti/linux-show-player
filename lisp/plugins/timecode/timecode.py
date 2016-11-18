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

from enum import Enum

from lisp.application import Application
from lisp.core.has_properties import Property
from lisp.core.plugin import Plugin
from lisp.core.signal import Connection
from lisp.cues.cue import Cue
from lisp.cues.cue_time import CueTime
from lisp.plugins.timecode.timecode_settings import TimecodeSettings
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.utils.util import time_tuple

__AVAILABLE__ = True
try:
    from ola.OlaClient import OLADNotRunningException, OlaClient
except ImportError:
    __AVAILABLE__ = False


class TimecodeHandler(CueTime):
    TC_DEF = [
        {'millis':1000/24, 'format':OlaClient.TIMECODE_FILM },
        {'millis':1000/25, 'format':OlaClient.TIMECODE_EBU },
        {'millis':1000/24, 'format':OlaClient.TIMECODE_SMPTE }
    ]

    def __init__(self, cue):
        global __AVAILABLE__
        super().__init__(cue)

        if __AVAILABLE__:
            self.__client = OlaClient()
            self.__cue = cue
            self.__conf = cue.timecode
            self.__connected = False

    def send_timecode(self, time):
        if __AVAILABLE__:
            tt = time_tuple(time)
            fmt = self.__conf['format']
            millis = self.TC_DEF[fmt]['millis']
            tcfmt = self.TC_DEF[fmt]['format']
            if self.__conf['use_hours']:
                print(tcfmt, self.__cue.index, tt[1], tt[2], round(tt[3]/millis))
                self.__client.SendTimeCode(tcfmt, self.__cue.index, tt[1], tt[2], round(tt[3]/millis), 0)
            else:
                print(tcfmt, tt[0], tt[1], tt[2], round(tt[3]/millis))
                self.__client.SendTimeCode(tcfmt, tt[0], tt[1], tt[2], round(tt[3]/millis), 0)

    def start_timecode(self):
        if self.__conf['enabled']:
            self.__connected = True
            self.notify.connect(self.send_timecode, Connection.QtQueued)

    def stop_timecode(self):
        if self.__connected:
            self.__connected = False
            self.notify.disconnect()

    def update_conf(self, timecode):
        self.__conf = timecode


class Timecode(Plugin):

    Name = "Timecode"
    
    def __init__(self):
        super().__init__()
        global __AVAILABLE__

        self.__handlers = {}

        # Register a new Cue property to store settings
        Cue.register_property('timecode', Property(default={}))

        # Register settings-page
        CueSettingsRegistry().add_item(TimecodeSettings)

        # Connect Timecode
        Application().cue_model.item_added.connect(self.__cue_added)
        Application().cue_model.item_removed.connect(self.__cue_removed)

    def init(self):
        global __AVAILABLE__
        try:
            client = OlaClient()
            del client
        except OLADNotRunningException:
            __AVAILABLE__ = False

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
        self.__handlers.pop(cue.id, None)

    def __cue_started(self, cue):
        if __AVAILABLE__:
            for key in self.__handlers:
                self.__handlers[key].stop_timecode()
            self.__handlers[cue.id].start_timecode()