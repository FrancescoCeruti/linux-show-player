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

from lisp.application import Application
from lisp.cues.cue import Cue


class RemoteDispatcher:
    # Layout functions

    def get_cue_at(self, index):
        cue = Application().layout.model_adapter.item(index)
        if cue is not None:
            return cue.properties()
        return {}

    def get_cues(self, cue_class=Cue):
        cues = Application().cue_model.filter(cue_class)
        return [cue.properties() for cue in cues]

    # Cue function

    def execute(self, index):
        cue = Application().layout.model_adapter.item(index)
        if cue is not None:
            cue.execute()
