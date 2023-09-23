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
    """Factory to build different cues types.

    Cues can be registered via `register_factory` function.
    """

    def __init__(self, app):
        self.app = app
        self.__registry = {}

    def register_factory(self, cue_type, factory):
        """Register a new cue-type in the factory.

        :param cue_type: The cue class name
        :type cue_type: str
        :param factory: The cue class, or a factory function
        """
        self.__registry[cue_type] = factory

    def has_factory(self, cue_type):
        """Return True if there is a factory for `cue_type`

        :param cue_type: The cue type to check
        :rtype cue_type: str
        :rtype: bool
        """
        return cue_type in self.__registry

    def remove_factory(self, cue_type):
        """Remove the registered cue from the factory

        :param cue_type: the cue class name (the same used for registration)
        """
        self.__registry.pop(cue_type)

    def create_cue(self, cue_type, cue_id=None, **kwargs):
        """Return a new cue of the specified type.

        ..note:
            Some factory can take keyword-arguments (e.g. URIAudio)

        :param cue_id: The id to use with the new cue
        :param cue_type: The cue type
        :rtype: lisp.cues.cue.Cue
        """
        factory = self.__registry.get(cue_type)

        if not callable(factory):
            raise Exception(
                f"Cue not available or badly registered: {cue_type}"
            )

        return factory(app=self.app, id=cue_id, **kwargs)

    def clone_cue(self, cue):
        """Return a copy of the given cue. The id is not copied.

        :param cue: the cue to be copied
        :rtype: lisp.cues.cue.Cue
        """
        properties = deepcopy(cue.properties())
        properties.pop("id")

        cue = self.create_cue(typename(cue))
        cue.update_properties(properties)

        return cue
