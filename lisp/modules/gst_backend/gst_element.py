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

from lisp.backend.media_element import MediaElement, ElementType
from lisp.core.has_properties import Property


class GstProperty(Property):

    def __init__(self, element_name, default=None, gst_name=None, adapter=None):
        super().__init__(default=default)

        self.element_name = element_name
        self.gst_name = gst_name
        self.adapter = adapter

    def __set__(self, instance, value):
        super().__set__(instance, value)

        if instance is not None:
            if self.adapter is not None:
                value = self.adapter(value)

            name = self.gst_name if self.gst_name is not None else self.name
            getattr(instance, self.element_name).set_property(name, value)


class GstRuntimeProperty:

    def __init__(self, element_name, property_name, adapter=None):
        self.element_name = element_name
        self.property_name = property_name
        self.adapter = adapter

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            element = getattr(instance, self.element_name)
            return element.get_property(self.property_name)

    def __set__(self, instance, value):
        if self.adapter is not None:
            value = self.adapter(value)
        getattr(instance, self.element_name).set_property(self.property_name,
                                                          value)


class GstMediaElement(MediaElement):
    """All the subclass must take the pipeline as first __init__ argument"""

    def interrupt(self):
        """Called before Media interrupt"""

    def stop(self):
        """Called before Media stop"""

    def pause(self):
        """Called before Media pause"""

    def play(self):
        """Called before Media play"""

    def dispose(self):
        """Clean up the element"""

    def sink(self):
        """Return the GstElement used as sink"""
        return None

    def src(self):
        """Return the GstElement used as src"""
        return None

    def link(self, element):
        if self.src() is not None:
            sink = element.sink()
            if sink is not None:
                return self.src().link(sink)
        return False

    def unlink(self, element):
        if self.src() is not None:
            sink = element.sink()
            if sink is not None:
                return self.src().unlink(sink)
        return False


class GstSrcElement(GstMediaElement):
    ElementType = ElementType.Input

    duration = Property(default=0)

    def input_uri(self):
        """Return the input uri or None"""
        return None