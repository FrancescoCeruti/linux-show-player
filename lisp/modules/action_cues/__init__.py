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

import logging

from lisp.core.module import Module
from lisp.modules.action_cues.action_cue_factory import ActionCueFactory
from lisp.utils.dyamic_loader import load_classes
from lisp.utils.util import file_path
from lisp.application import Application
from lisp.ui.mainwindow import MainWindow
from lisp.cues.cue_factory import CueFactory


class ActionCues(Module):

    def __init__(self):
        super().__init__()

        # Register the ActionCueFactory
        CueFactory.register_factory('ActionCue', ActionCueFactory)

        for cue_name, cue_class in load_classes(file_path(__file__, 'cues')):
            # Register the single action in the action factory
            ActionCueFactory.register_action_cue(cue_class)
            # Register the menu action for adding the action-cue
            add_function = ActionCues.create_add_action_cue_method(cue_class)
            MainWindow().register_cue_menu_action(cue_class.Name, add_function,
                                                  'Action cues')

            logging.debug('ACTION-CUES: Loaded "' + cue_name + '"')

    @staticmethod
    def create_add_action_cue_method(cue_class):
        def method():
            cue = ActionCueFactory.create_cue(cue_class.__name__)
            cue.name = cue_class.Name
            Application().layout.add_cue(cue)

        return method
