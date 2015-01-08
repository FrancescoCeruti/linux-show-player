##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################


from PyQt5.QtCore import QObject
from lisp.core.plugin import Plugin

from lisp.application import Application
from lisp.modules import check_module
from lisp.modules.midi.midi import InputMidiHandler

from .controller_settings import ControllerSettings


class Controller(QObject, Plugin):

    Name = 'Controller'

    def __init__(self):
        super().__init__()

        self.__map = {}

        self.app = Application()
        self.app.layout.key_pressed.connect(self.on_key_pressed)
        self.app.layout.cue_added.connect(self.on_cue_added)
        self.app.layout.cue_removed.connect(self.on_cue_removed)
        self.app.layout.add_settings_section(ControllerSettings)

        if check_module('midi'):
            InputMidiHandler().new_message.connect(self.on_new_message)

    def reset(self):
        self.app.layout.key_pressed.disconnect(self.on_key_pressed)
        self.app.layout.cue_added.disconnect(self.on_cue_added)
        self.app.layout.cue_removed.disconnect(self.on_cue_removed)
        self.app.layout.remove_settings_section(ControllerSettings)

        self.__map = {}

    def update_map(self, cue):
        self.delete_from_map(cue)

        if 'hotkeys' in cue.properties():
            if len(cue['hotkeys']) > 0:
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
        cue.updated.connect(self.update_map)
        self.update_map(cue)

    def on_cue_removed(self, cue):
        cue.updated.disconnect(self.update_map)
        self.delete_from_map(cue)
