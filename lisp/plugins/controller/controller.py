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


from PyQt5.QtCore import QObject

from lisp.application import Application
from lisp.core.has_properties import Property
from lisp.core.plugin import Plugin
from lisp.cues.cue import Cue
from lisp.modules import check_module
from lisp.modules.midi.input_handler import MIDIInputHandler
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from .controller_settings import ControllerSettings


class Controller(Plugin):

    Name = 'Controller'

    def __init__(self):
        super().__init__()
        self.__map = {}

        # Register a new Cue property to store settings
        Cue.register_property('controller', Property(default={}))

        # Listen cue_model changes
        Application().cue_model.item_added.connect(self.on_cue_added)
        Application().cue_model.item_removed.connect(self.on_cue_removed)

        # Register settings-page
        CueSettingsRegistry().add_item(ControllerSettings)

        # Connect to MIDI module
        if check_module('midi'):
            MIDIInputHandler().new_message.connect(self.on_new_message)

    def init(self):
        Application().layout.key_pressed.connect(self.on_key_pressed)

    def reset(self):
        self.__map.clear()
        Application().layout.key_pressed.disconnect(self.on_key_pressed)

    def cue_changed(self, cue, property_name, value):
        if property_name == 'controller':
            self.delete_from_map(cue)

            for key in value.get('hotkeys', []):
                if key not in self.__map:
                    self.__map[key] = [cue]
                else:
                    self.__map[key].append(cue)

            if value.get('midi', '') != '':
                if not value['midi'] in self.__map:
                    self.__map[value['midi']] = [cue]
                else:
                    self.__map[value['midi']].append(cue)

    def delete_from_map(self, cue):
        for key in self.__map:
            try:
                self.__map[key].remove(cue)
            except ValueError:
                pass

    def on_key_pressed(self, keyEvent):
        self.perform_action(keyEvent.text())

    def on_new_message(self, message):
        self.perform_action(str(message))

    def perform_action(self, key):
        for cue in self.__map.get(key, []):
            cue.execute()

    def on_cue_added(self, cue):
        cue.property_changed.connect(self.cue_changed)
        #self.update_map(cue)

    def on_cue_removed(self, cue):
        cue.property_changed.disconnect(self.cue_changed)
        self.delete_from_map(cue)
