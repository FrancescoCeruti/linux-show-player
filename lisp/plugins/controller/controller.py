# This file is part of Linux Show Player
#
# Copyright 2018 Francesco Ceruti <ceppofrancy@gmail.com>
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
from lisp.plugins.controller.common import LayoutAction
from lisp.plugins.controller.controller_settings import (
    CueControllerSettingsPage,
    ControllerLayoutConfiguration,
)
from lisp.ui.settings.app_configuration import AppConfigurationDialog
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)


class Controller(Plugin):
    Name = "Controller"
    Authors = ("Francesco Ceruti", "Thomas Achtner")
    OptDepends = ("Midi", "Osc")
    Description = (
        "Allow to control cues via external commands with multiple " "protocols"
    )

    def __init__(self, app):
        super().__init__(app)

        self.__cue_map = {}
        self.__global_map = {}
        self.__protocols = {}

        # Register a new Cue property to store settings
        Cue.controller = Property(default={})

        # On session created/destroy
        self.app.session_created.connect(self.session_init)
        self.app.session_before_finalize.connect(self.session_reset)

        # Listen cue_model changes
        self.app.cue_model.item_added.connect(self.__cue_added)
        self.app.cue_model.item_removed.connect(self.__cue_removed)

        # Register the settings widget
        AppConfigurationDialog.registerSettingsPage(
            "plugins.controller",
            ControllerLayoutConfiguration,
            Controller.Config,
        )
        # Register settings-page
        CueSettingsRegistry().add(CueControllerSettingsPage)

        # Load available protocols
        self.__load_protocols()

        self.global_changed(Controller.Config)
        Controller.Config.updated.connect(self.global_changed)
        Controller.Config.changed.connect(self.global_changed)

    def session_init(self):
        for protocol in self.__protocols.values():
            protocol.init()

    def session_reset(self):
        self.__cue_map.clear()

        for protocol in self.__protocols.values():
            protocol.reset()

    def global_changed(self, *args):
        # Here we just rebuild everything which is not the best solution
        # but is the easiest
        self.__global_map = {}
        for protocol in Controller.Config["protocols"].values():
            for key, action in protocol:
                self.__global_map.setdefault(key, set()).add(
                    LayoutAction(action)
                )

    def cue_changed(self, cue, property_name, value):
        if property_name == "controller":
            self.delete_from_cue_map(cue)

            for protocol in self.__protocols:
                for key, action in value.get(protocol, ()):
                    actions_map = self.__cue_map.setdefault(key, {})
                    actions_map.setdefault(cue, set()).add(CueAction(action))

    def delete_from_cue_map(self, cue):
        for actions_map in self.__cue_map.values():
            actions_map.pop(cue)

    def perform_cue_action(self, key):
        for cue, actions in self.__cue_map.get(key, {}).items():
            for action in actions:
                cue.execute(action)

    def perform_session_action(self, key):
        for action in self.__global_map.get(key, ()):
            if action is LayoutAction.Go:
                self.app.layout.go()
            elif action is LayoutAction.Reset:
                self.app.layout.interrupt_all()
                self.app.layout.set_standby_index(0)
            elif action is LayoutAction.StopAll:
                self.app.layout.stop_all()
            elif action is LayoutAction.PauseAll:
                self.app.layout.pause_all()
            elif action is LayoutAction.ResumeAll:
                self.app.layout.resume_all()
            elif action is LayoutAction.InterruptAll:
                self.app.layout.interrupt_all()
            elif action is LayoutAction.FadeOutAll:
                self.app.layout.fadeout_all()
            elif action is LayoutAction.FadeInAll:
                self.app.layout.fadeout_all()
            elif action is LayoutAction.StandbyForward:
                self.app.layout.set_standby_index(
                    self.app.layout.standby_index() + 1
                )
            elif action is LayoutAction.StandbyBack:
                self.app.layout.set_standby_index(
                    self.app.layout.standby_index() - 1
                )
            else:
                self.app.finalize()

    def __cue_added(self, cue):
        cue.property_changed.connect(self.cue_changed)
        self.cue_changed(cue, "controller", cue.controller)

    def __cue_removed(self, cue):
        cue.property_changed.disconnect(self.cue_changed)
        self.delete_from_cue_map(cue)

    def __load_protocols(self):
        protocols.load()

        for protocol_class in protocols.Protocols:
            try:
                protocol = protocol_class()
                protocol.protocol_event.connect(self.perform_cue_action)
                protocol.protocol_event.connect(self.perform_session_action)

                self.__protocols[protocol_class.__name__.lower()] = protocol
            except Exception:
                logger.exception(
                    translate(
                        "Controller", 'Cannot load controller protocol: "{}"'
                    ).format(protocol_class.__name__)
                )
