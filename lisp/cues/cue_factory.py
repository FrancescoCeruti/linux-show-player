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

from copy import deepcopy


class CueFactory:
    """Provide a factory for build different cues types.

    Any cue must be register, via register_factory function.
    """

    _REGISTRY_ = {}

    # Register methods

    @classmethod
    def register_factory(cls, cue_type, factory):
        """
        Register a new cue-type in the factory.

        :param cue_type: The cue class name
        :type cue_type: str
        :param factory: The cue class or a factory function

        """
        cls._REGISTRY_[cue_type] = factory

    @classmethod
    def remove_factory(cls, cue_type):
        """
        Remove the registered cue from the factory

        :param cue_type: the cue class name (the same used for registration)
        """
        cls._REGISTRY_.pop(cue_type)

    # Create methods

    @classmethod
    def create_cue(cls, cue_type, **kwargs):
        """
        Return a new cue of the specified type.

        ..note:
            Some factory can take keyword-arguments (e.g. URIAudio)

        :param cue_type: The cue type
        """
        factory = cls._REGISTRY_.get(cue_type, None)

        if not callable(factory):
            raise Exception('Cue not available or badly registered: ' + str(cue_type))

        return factory(**kwargs)

    @classmethod
    def clone_cue(cls, cue, same_id=False):
        """
        Return a copy of the given cue.

        ..warning:
            Using the same id can cause a lot of problems, use it only if the copied cue will be destroyed
            after the copy (e.g. a finalized cue).

        :param cue: the cue to be copied
        :param same_id: if True the new cue is created with the same id
        """
        properties = deepcopy(cue.properties())
        cue = cls.create_cue(cue.__class__.__name__)

        if not same_id:
            properties.pop('id')

        cue.update_properties(properties)

        return cue
