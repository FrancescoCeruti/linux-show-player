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

from lisp.core.signal import Signal


class HasProperties:
    """Base class providing a simple way to mange object properties.

    Using the _property_ attribute, subclasses can specify a set of properties,
    those can be easily retrieved and updated via :func:`properties` and
    :func:`update_properties`.

    .. Usage::

        class MyClass(BaseClass):
            _properties_ = ('p1', 'p2')

            def __init__(self):
                super().__init__()
                self.p1 = 0
                self.__p2 = 0

            @property
            def p2(self):
                return self.__p2

            @p2.setter
            def p2(self, value):
                self.__p2 = value

        obj = MyClass()
        obj.p1 = 10
        obj.p2 = 20
        obj.update_properties({'p1': 5, 'p2': 3})
    """

    _properties_ = ()

    def __init__(self):
        #: Emitted after property change (name, value)
        self.property_changed = Signal()

        self.__changed_signals = {}
        """
        Contains signals that are emitted after the associated property is
        changed, the signal are create only when required the first time.
        """

    def changed(self, property_name):
        """
        :param property_name: The property name
        :return: The property change-signal
        :rtype: Signal
        """
        if property_name not in self._properties_:
            raise ValueError('no property "{0}"'.format(property_name))

        signal = self.__changed_signals.get(property_name, None)

        if signal is None:
            signal = Signal()
            self.__changed_signals[property_name] = signal

        return signal

    def properties(self):
        """
        :return: The properties as a dictionary {name: value}
        :rtype: dict
        """
        return {name: getattr(self, name, None) for name in self._properties_}

    def update_properties(self, properties):
        """Set the given properties.

        :param properties: The element properties
        :type properties: dict
        """
        for name, value in properties.items():
            if name in self._properties_:
                setattr(self, name, value)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

        if key in self._properties_:
            self.property_changed.emit(key, value)
            # Get the related signal
            property_signal = self.__changed_signals.get(key, None)
            if property_signal is not None:
                property_signal.emit(value)
