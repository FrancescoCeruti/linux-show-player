# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2018 Francesco Ceruti <ceppofrancy@gmail.com>
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

from lisp.core.plugin import Plugin
from lisp.core.properties import Property
from lisp.cues.cue import Cue, CueAction
from lisp.plugins.controller import protocols
from lisp.plugins.controller.controller_settings import ControllerSettings
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)


class Controller(Plugin):
    Name = 'Controller'
    Authors = ('Francesco Ceruti', 'Thomas Achtner')
    OptDepends = ('Midi', 'Osc')
    Description = 'Allow to control cues via external commands with multiple ' \
                  'protocols'

    def __init__(self, app):
        super().__init__(app)

        self.__map = {}
        self.__actions_map = {}
        self.__protocols = {}

        # Register a new Cue property to store settings
        Cue.controller = Property(default={})

        # On session created/destroy
        self.app.session_created.connect(self.session_init)
        self.app.session_before_finalize.connect(self.session_reset)

        # Listen cue_model changes
        self.app.cue_model.item_added.connect(self.__cue_added)
        self.app.cue_model.item_removed.connect(self.__cue_removed)

        # Register settings-page
        CueSettingsRegistry().add(ControllerSettings)

        # Load available protocols
        self.__load_protocols()

    def session_init(self):
        for protocol in self.__protocols.values():
            protocol.init()

    def session_reset(self):
        self.__map.clear()
        self.__actions_map.clear()

        for protocol in self.__protocols.values():
            protocol.reset()

    def cue_changed(self, cue, property_name, value):
        if property_name == 'controller':
            self.delete_from_map(cue)

            for protocol in self.__protocols:
                for key, action in value.get(protocol, []):
                    if key not in self.__map:
                        self.__map[key] = set()

                    self.__map[key].add(cue)
                    self.__actions_map[(key, cue)] = CueAction(action)

    def delete_from_map(self, cue):
        for key in self.__map:
            self.__map[key].discard(cue)
            self.__actions_map.pop((key, cue), None)

    def perform_action(self, key):
        for cue in self.__map.get(key, []):
            cue.execute(self.__actions_map[(key, cue)])

    def __cue_added(self, cue):
        cue.property_changed.connect(self.cue_changed)
        self.cue_changed(cue, 'controller', cue.controller)

    def __cue_removed(self, cue):
        cue.property_changed.disconnect(self.cue_changed)
        self.delete_from_map(cue)

    def __load_protocols(self):
        protocols.load()

        for protocol_class in protocols.Protocols:
            try:
                protocol = protocol_class()
                protocol.protocol_event.connect(self.perform_action)

                self.__protocols[protocol_class.__name__.lower()] = protocol
            except Exception:
                logger.exception(
                    translate(
                        'Controller', 'Cannot load controller protocol: "{}"'
                    ).format(protocol_class.__name__)
                )
