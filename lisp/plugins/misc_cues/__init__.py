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

from os import path

from lisp.core.loading import load_classes
from lisp.core.plugin import Plugin
from lisp.cues.cue_factory import CueFactory
from lisp.ui.ui_utils import translate


class MiscCues(Plugin):
    Name = "Miscellaneous Cues"
    Authors = ("Various",)
    Description = "A collection of cues that don't belong to specific plugins"

    def __init__(self, app):
        super().__init__(app)

        for name, cue in load_classes(__package__, path.dirname(__file__)):
            # Register the action-cue in the cue-factory
            CueFactory.register_cue_type(self.app, cue)
