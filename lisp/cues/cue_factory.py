# This file is part of Linux Show Player
#
# Copyright 2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

from lisp.core.util import typename


class CueFactory:
    """Provide a generic factory to build different cues types.

    Cues can be register via `register_factory` function.
    """

    __REGISTRY = {}

    # Register methods

    @classmethod
    def register_factory(cls, cue_type, factory):
        """Register a new cue-type in the factory.

        :param cue_type: The cue class name
        :type cue_type: str
        :param factory: The cue class or a factory function
        """
        cls.__REGISTRY[cue_type] = factory

    @classmethod
    def has_factory(cls, cue_type):
        """Return True if there is a factory for `cue_type`

        :param cue_type: The cue type to check
        :rtype cue_type: str
        :rtype: bool
        """
        return cue_type in cls.__REGISTRY

    @classmethod
    def remove_factory(cls, cue_type):
        """Remove the registered cue from the factory

        :param cue_type: the cue class name (the same used for registration)
        """
        cls.__REGISTRY.pop(cue_type)

    # Create methods

    @classmethod
    def create_cue(cls, cue_type, cue_id=None, **kwargs):
        """Return a new cue of the specified type.

        ..note:
            Some factory can take keyword-arguments (e.g. URIAudio)

        :param cue_id: The id to use with the new cue
        :param cue_type: The cue type
        :rtype: lisp.cues.cue.Cue
        """
        factory = cls.__REGISTRY.get(cue_type)

        if not callable(factory):
            raise Exception(
                "Cue not available or badly registered: {}".format(cue_type)
            )

        return factory(id=cue_id, **kwargs)

    @classmethod
    def clone_cue(cls, cue):
        """Return a copy of the given cue. The id is not copied.

        :param cue: the cue to be copied
        :rtype: lisp.cues.cue.Cue
        """
        properties = deepcopy(cue.properties())
        properties.pop("id")

        cue = cls.create_cue(typename(cue))
        cue.update_properties(properties)

        return cue
