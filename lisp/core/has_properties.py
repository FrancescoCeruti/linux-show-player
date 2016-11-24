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
from copy import deepcopy

from lisp.core.signal import Signal
from lisp.core.util import subclasses


class Property:
    """Descriptor to be used in HasProperties subclasses to define properties.

    .. warning::
        To be able to save properties into a session, the stored value
        MUST be JSON-serializable.

    .. warning::
        If extended any subclass *MUST*:
        1) if the __get__ method receive a None instance return self;
        2) if the __get__ is called while the value is not set, set it with a
           safe copy of 'default' and return.
        3) After the value is changed call the __changed__ method.
    """

    def __init__(self, default=None):
        self.name = 'unnamed_property'
        self.default = default

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        elif self.name not in instance.__dict__:
            instance.__dict__[self.name] = deepcopy(self.default)

        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        if instance is not None:
            # Only change the value if different
            if value != instance.__dict__.get(self.name, self.default):
                instance.__dict__[self.name] = value
                self.__changed__(instance, value)

    def changed(self, instance):
        if instance is not None:
            value = self.__get__(instance)
            return value != self.default, value

        return False, self.default

    def __changed__(self, instance, value):
        instance.property_changed.emit(instance, self.name, value)
        # Get the related signal
        property_signal = instance.changed_signals.get(self.name)
        if property_signal is not None:
            property_signal.emit(value)


class WriteOnceProperty(Property):
    """Property that can be modified only once.

    Obviously this is not really "write-once", but if used as normal attribute
    will ignore any change when the stored value is different from default.
    """

    def __set__(self, instance, value):
        if self.__get__(instance) == self.default:
            super().__set__(instance, value)


class NestedProperties(Property):
    """Simplify retrieving the properties of nested HasProperties objects.

    The goal is to avoid the reimplementation of HasProperties.properties()
    and HasProperties.update_properties().

    ..note::
        When getting or setting a single property of the nested object is better
        to access it directly instead that using the nested-property.
    """

    def __init__(self, provider_name, default=None):
        super().__init__(default=default)
        self.provider_name = provider_name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        else:
            provider = instance.__dict__.get(self.provider_name)
            if isinstance(provider, HasProperties):
                return provider.properties()

    def __set__(self, instance, value):
        if instance is not None:
            provider = instance.__dict__.get(self.provider_name)
            if isinstance(provider, HasProperties):
                provider.update_properties(value)
                self.__changed__(instance, value)

    def changed(self, instance):
        if instance is not None:
            provider = instance.__dict__.get(self.provider_name)
            if isinstance(provider, HasProperties):
                properties = provider.properties(only_changed=True)
                # If no properties is changed (empty dict) return false
                return bool(properties), properties

        return False, {}


class HasPropertiesMeta(ABCMeta):
    """Metaclass for HasProperties classes.

    This metaclass manage the 'propagation' of the properties in all subclasses,
    this process involves overwriting __properties__ with a set containing all
    the properties names.

    ..note::
        This metaclass is derived form :class:`abc.ABCMeta`, so abstract
        classes can be created without using an intermediate metaclass
    """

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Use a set for avoiding repetitions
        cls.__properties__ = set()

        # Populate with all the properties
        for name, attribute in vars(cls).items():
            if isinstance(attribute, Property):
                cls.__properties__.add(name)
                attribute.name = name

        for base in cls.__bases__:
            cls.__properties__.update(getattr(base, '__properties__', ()))


class HasProperties(metaclass=HasPropertiesMeta):
    """Base class providing a simple way to mange object properties.

    Using the Property descriptor, subclasses, can specify a set of
    properties, that can be easily retrieved and updated via :func:`properties`
    and :func:`update_properties`.

    .. Usage::

        class MyClass(HasProperties):
            prop1 = Property(default=100)
            prop2 = Property()
    """

    __properties__ = set()

    def __init__(self):
        self.property_changed = Signal()
        #: Emitted after property change (self, name, value)

        self.changed_signals = {}
        """Contains signals that are emitted after the associated property is
        changed, the signal are create only when requested the first time.
        """

    @classmethod
    def register_property(cls, name, prop):
        """Register a new property with the given name.

        :param str name: Property name
        :param BaseProperty prop: The property
        """
        if name not in cls.__properties__:
            prop.name = name
            setattr(cls, name, prop)
            cls.__properties__.add(name)

            for subclass in subclasses(cls):
                subclass.__properties__.add(name)

    def changed(self, property_name):
        """
        :param property_name: The property name
        :return: The property change-signal
        :rtype: Signal
        """
        if property_name not in self.__class__.__properties__:
            raise ValueError('no property "{0}" found'.format(property_name))

        signal = self.changed_signals.get(property_name, None)

        if signal is None:
            signal = Signal()
            self.changed_signals[property_name] = signal

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
            for name in self.__properties__:
                changed, value = getattr(self.__class__, name).changed(self)
                if changed:
                    properties[name] = value

            return properties

        return {name: getattr(self, name) for name in self.__properties__}

    @classmethod
    def properties_defaults(cls):
        """
        :return: The default properties as a dictionary {name: default_value}
        :rtype: dict
        """
        return {name: getattr(cls, name).default for name in cls.__properties__}

    def update_properties(self, properties):
        """Set the given properties.

        :param properties: The element properties
        :type properties: dict
        """
        for name, value in properties.items():
            if name in self.__properties__:
                setattr(self, name, value)
