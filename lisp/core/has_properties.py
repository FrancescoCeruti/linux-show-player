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

from abc import ABCMeta

from lisp.core.properties import Property, LiveProperty
from lisp.core.signal import Signal
from lisp.core.util import subclasses


class HasPropertiesMeta(ABCMeta):
    """Metaclass for HasProperties classes.

    This metaclass manage the "propagation" of the properties in all subclasses.

    ..note::
        This metaclass is derived form :class:`abc.ABCMeta`, so abstract
        classes can be created without using an intermediate metaclass
    """

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.__properties__ = set()
        cls.__live_properties__ = set()

        # Populate with the existing properties
        for name, attribute in vars(cls).items():
            if isinstance(attribute, Property):
                cls.__properties__.add(name)
                attribute.name = name
            elif isinstance(attribute, LiveProperty):
                cls.__live_properties__.add(name)
                attribute.name = name

        for base in cls.__bases__:
            if isinstance(base, HasPropertiesMeta):
                cls.__properties__.update(base.__properties__)
                cls.__live_properties__.update(base.__live_properties__)

    def __setattr__(cls, name, value):
        super().__setattr__(name, value)

        if isinstance(value, Property):
            cls.__properties__.add(name)
            value.name = name

            for subclass in subclasses(cls):
                subclass.__properties__.add(name)
        elif isinstance(value, LiveProperty):
            cls.__live_properties__.add(name)
            value.name = name

            for subclass in subclasses(cls):
                subclass.__live_properties__.add(name)

    def __delattr__(cls, name):
        super().__delattr__(name)

        cls.__properties__.discard(name)
        cls.__live_properties__.discard(name)

        for subclass in subclasses(cls):
            subclass.__properties__.discard(name)
            subclass.__live_properties__.discard(name)


class HasProperties(metaclass=HasPropertiesMeta):
    """Base class providing a simple way to mange object properties.

    Using the Property descriptor, subclasses, can specify a set of
    properties, that can be easily retrieved and updated via :func:`properties`
    and :func:`update_properties`.

    When using LiveProperty those should be named as the "non-live" counterpart
    prefixed by "live_".

    .. Usage::

        class MyClass(HasProperties):
            prop1 = Property(default=100)
            prop2 = Property()

            live_prop1 = ConcreteLiveProperty()
    """

    __properties__ = set()
    __live_properties__ = set()

    def __init__(self):
        self._changed_signals = {}
        # Contains signals that are emitted after the associated property is
        # changed, the signal are create only when requested the first time.

        self.property_changed = Signal()
        # Emitted after property change (self, name, value)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)

        if name in self.properties_names():
            self.property_changed.emit(self, name, value)
            self.__emit_changed(name, value)
        elif name in self.live_properties_names():
            self.__emit_changed(name, value)

    def __emit_changed(self, name, value):
        try:
            self._changed_signals[name].emit(value)
        except KeyError:
            pass

    @classmethod
    def register_property(cls, name, prop):
        """Register a new property with the given name.

        :param name: Property name
        :param prop: The property

        _Deprecated: use normal attribute assignment for the class_
        """
        setattr(cls, name, prop)

    def changed(self, name):
        """
        :param name: The property name
        :return: The property change-signal
        :rtype: Signal
        """
        if (name not in self.properties_names() and
                name not in self.live_properties_names()):
            raise ValueError('no property "{}" found'.format(name))

        signal = self._changed_signals.get(name)

        if signal is None:
            signal = Signal()
            self._changed_signals[name] = signal

        return signal

    def properties(self, only_changed=False):
        """
        :param only_changed: when True only "changed" properties are collected
        :type only_changed: bool

        :return: The properties as a dictionary {name: value}
        :rtype: dict
        """
        if only_changed:
            properties = {}
            for name in self.properties_names():
                changed, value = getattr(self.__class__, name).changed(self)
                if changed:
                    properties[name] = value

            return properties

        return {name: getattr(self, name) for name in self.properties_names()}

    def update_properties(self, properties):
        """Set the given properties.

        :param properties: The element properties
        :type properties: dict
        """
        for name, value in properties.items():
            if name in self.properties_names():
                setattr(self, name, value)

    @classmethod
    def properties_defaults(cls):
        """
        :return: The default properties as a dictionary {name: default_value}
        :rtype: dict
        """
        return {name: getattr(cls, name).default for name in cls.__properties__}

    @classmethod
    def properties_names(cls):
        """Retrieve properties names from the class

        :return: A set containing the properties names
        :rtype: set[str]
        """
        return cls.__properties__

    @classmethod
    def live_properties_names(cls):
        return cls.__live_properties__
