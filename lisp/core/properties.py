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

from copy import deepcopy
from weakref import WeakKeyDictionary


class Property:
    """Descriptor used to define properties.

    Properties allow to define "special" attributes for objects, to provide
    custom behaviors in a simple and reusable manner.

    Should be used in combination with an HasProperties object.

    As default value list, dict and likely can be used, since the default value
    is (deep)copied.

    Warning:
        To be able to save properties into a session, the stored value
        MUST be JSON-serializable.

    Note:
        Internally a WeakKeyDictionary is used, to avoid keeping objects
        references alive
    """

    def __init__(self, default=None, **meta):
        self._values = WeakKeyDictionary()

        self.default = default
        self.meta = meta

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        elif instance not in self._values:
            self._values[instance] = deepcopy(self.default)

        return self._values[instance]

    def __set__(self, instance, value):
        if instance is not None:
            self._values[instance] = value


class WriteOnceProperty(Property):
    """Property that can be modified only once.

    Obviously this is not really "write-once", but when used as normal attribute
    will ignore any change when the stored value is different than the default.
    """

    def __set__(self, instance, value):
        if self.__get__(instance) == self.default:
            super().__set__(instance, value)


class InstanceProperty:
    """Per-instance property, not a descriptor.

    To be of any use an InstanceProperty should be used in combination
    of an HasInstanceProperties object.
    """
    __slots__ = ('value', 'default')

    def __init__(self, default=None):
        self.value = default
        self.default = default

    def __pget__(self):
        return self.value

    def __pset__(self, value):
        self.value = value