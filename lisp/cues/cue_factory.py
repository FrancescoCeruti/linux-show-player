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


class CueFactory:
    """Provide a generic-factory for build different cues types.

    Any cue must register his factory.
    """

    __REGISTRY = {}

    # Register methods

    @classmethod
    def register_factory(cls, cue_type, factory):
        cls.__REGISTRY[cue_type] = factory

    @classmethod
    def remove_factory(cls, cue_type):
        cls.__REGISTRY.pop(cue_type)

    # Create methods

    @classmethod
    def create_cue(cls, cue_type, **kwargs):
        factory = cls.__REGISTRY.get(cue_type, None)

        if factory is None:
            raise Exception('Cue not available: ' + str(cue_type))

        return factory.create_cue(**kwargs)

    @classmethod
    def clone_cue(cls, cue, same_id=False):
        if not same_id:
            properties = cue.properties().copy()
            properties.pop('id')
            return cls.create_cue(properties)
        else:
            return cls.create_cue(cue.properties())
