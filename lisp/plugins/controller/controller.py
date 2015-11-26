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


from PyQt5.QtCore import QObject

from lisp.application import Application
from lisp.core.plugin import Plugin
from lisp.modules import check_module
from lisp.modules.midi.input_handler import MIDIInputHandler
from .controller_settings import ControllerSettings


class Controller(QObject, Plugin):

    Name = 'Controller'

    def __init__(self):
        super().__init__()

        self.__map = {}

        self.app = Application()
        self.app.layout.key_pressed.connect(self.on_key_pressed)
        self.app.cue_model.item_added.connect(self.on_cue_added)
        self.app.cue_model.item_removed.connect(self.on_cue_removed)
        self.app.layout.add_settings_section(ControllerSettings)

        if check_module('midi'):
            MIDIInputHandler().new_message.connect(self.on_new_message)

    def reset(self):
        self.app.layout.key_pressed.disconnect(self.on_key_pressed)
        self.app.cue_model.item_added.disconnect(self.on_cue_added)
        self.app.cue_model.item_removed.disconnect(self.on_cue_removed)
        self.app.layout.remove_settings_section(ControllerSettings)

        self.__map = {}

    def update_map(self, cue):
        self.delete_from_map(cue)

        if 'hotkeys' in cue.properties():
            if cue['hotkeys']:
                for key in cue['hotkeys']:
                    if key not in self.__map:
                        self.__map[key] = [cue]
                    else:
                        self.__map[key].append(cue)

        if 'midi' in cue.properties():
            if cue['midi'] != '':
                if not cue['midi'] in self.__map:
                    self.__map[cue['midi']] = [cue]
                else:
                    self.__map[cue['midi']].append(cue)

    def delete_from_map(self, cue):
        for key in self.__map:
            try:
                self.__map[key].remove(cue)
            except Exception:
                pass

    def on_key_pressed(self, keyEvent):
        self.perform_action(keyEvent.text())

    def on_new_message(self, message):
        self.perform_action(str(message))

    def perform_action(self, key):
        for cue in self.__map.get(key, []):
            cue.execute()

    def on_cue_added(self, cue):
        #cue.updated.connect(self.update_map)
        self.update_map(cue)

    def on_cue_removed(self, cue):
        #cue.updated.disconnect(self.update_map)
        self.delete_from_map(cue)
