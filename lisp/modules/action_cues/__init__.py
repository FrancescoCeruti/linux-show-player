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
from lisp.core.module import Module
from lisp.cues.cue_factory import CueFactory
from lisp.ui.mainwindow import MainWindow
from lisp.utils.dyamic_loader import ClassesLoader
from lisp.utils.util import translate


class ActionCues(Module):

    def __init__(self):
        for cue_name, cue_class in ClassesLoader(path.dirname(__file__)):
            # Register the action-cue in the cue-factory
            CueFactory.register_factory(cue_class.__name__, cue_class)
            # Register the menu action for adding the action-cue
            add_function = ActionCues.create_add_action_cue_method(cue_class)
            MainWindow().register_cue_menu_action(
                translate('CueName', cue_class.Name),
                add_function,
                'Action cues')

            logging.debug('ACTION-CUES: Loaded "' + cue_name + '"')

    @staticmethod
    def create_add_action_cue_method(cue_class):
        def method():
            cue = CueFactory.create_cue(cue_class.__name__)
            Application().cue_model.add(cue)

        return method
