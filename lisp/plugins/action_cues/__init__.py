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

import logging
from os import path

from lisp.application import Application
from lisp.core.loading import load_classes
from lisp.core.plugin import Plugin
from lisp.cues.cue_factory import CueFactory
from lisp.ui.ui_utils import translate


class ActionCues(Plugin):

    Name = 'Action Cues'
    Authors = ('Francesco Ceruti', )
    Description = 'Provide a collection of cues for different purposes'

    def __init__(self, app):
        super().__init__(app)

        for name, cue in load_classes(__package__, path.dirname(__file__)):
            # Register the action-cue in the cue-factory
            CueFactory.register_factory(cue.__name__, cue)

            # Register the menu action for adding the action-cue
            add_function = self.create_add_action_cue_function(cue)
            self.app.window.register_cue_menu_action(
                translate('CueName', cue.Name),
                add_function, 'Action cues')

            logging.debug('ACTION-CUES: Loaded "' + name + '"')

    def create_add_action_cue_function(self, cue_class):
        def function():
            try:
                cue = CueFactory.create_cue(cue_class.__name__)
                self.app.cue_model.add(cue)
            except Exception:
                # TODO: Display a message to the user
                import logging, traceback
                logging.error('Cannot create cue {}', cue_class.__name__)
                logging.debug(traceback.format_exc())

        return function
