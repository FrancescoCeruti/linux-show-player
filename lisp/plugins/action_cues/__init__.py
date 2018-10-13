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
from os import path

from lisp.core.loading import load_classes
from lisp.core.plugin import Plugin
from lisp.cues.cue_factory import CueFactory
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)


class ActionCues(Plugin):
    Name = 'Action Cues'
    Authors = ('Francesco Ceruti',)
    Description = 'Provide a collection of cues for different purposes'

    def __init__(self, app):
        super().__init__(app)

        for name, cue in load_classes(__package__, path.dirname(__file__)):
            # Register the action-cue in the cue-factory
            CueFactory.register_factory(cue.__name__, cue)

            # Register the menu action for adding the action-cue
            self.app.window.register_cue_menu_action(
                translate('CueName', cue.Name),
                self._new_cue_factory(cue),
                'Action cues'
            )

            logger.debug(translate(
                'ActionCuesDebug', 'Registered cue: "{}"').format(name))

    def _new_cue_factory(self, cue_class):
        def cue_factory():
            try:
                cue = CueFactory.create_cue(cue_class.__name__)
                self.app.cue_model.add(cue)
            except Exception:
                logger.exception(translate(
                    'ActionsCuesError',
                    'Cannot create cue {}').format(cue_class.__name__)
                )

        return cue_factory
