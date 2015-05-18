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


class ActionCueFactory:

    __REGISTRY = {}

    @classmethod
    def create_cue(cls, cue_type=None):
        cue_class = cls.__REGISTRY.get(cue_type, None)

        if cue_class is None:
            raise ValueError('undefined action-cue type: {0}'.format(cue_type))

        return cue_class()

    @classmethod
    def register_action_cue(cls, cue_class):
        cls.__REGISTRY[cue_class.__name__] = cue_class
