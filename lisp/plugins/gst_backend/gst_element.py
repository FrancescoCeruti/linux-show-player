# This file is part of Linux Show Player
#
# Copyright 2024 Francesco Ceruti <ceppofrancy@gmail.com>
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

from collections.abc import Collection
from typing import Union, Optional

from lisp.backend.media_element import MediaElement, ElementType
from lisp.core.has_properties import HasInstanceProperties
from lisp.core.properties import Property, InstanceProperty
from lisp.core.session_uri import SessionURI
from lisp.core.util import typename
from lisp.plugins.gst_backend.gst_fader import GstFader
from lisp.plugins.gst_backend.gst_properties import GstPropertyController


class GstMediaElement(MediaElement):
    """All the subclass must take the pipeline as first __init__ argument"""

    def __init__(self, pipeline):
        super().__init__()
        self.pipeline = pipeline

    def play(self):
        """Called before Media play"""

    def pause(self):
        """Called before Media pause"""

    def stop(self):
        """Called before Media stop"""

    def eos(self):
        """Called after Media ends. Defaults to `stop()`"""
        self.stop()

    def interrupt(self):
        """Called before Media interrupt. Defaults to `stop()`"""
        self.stop()

    def dispose(self):
        """Clean up the element"""

    def sink(self):
        """Return the GstElement used as sink"""
        return None

    def src(self):
        """Return the GstElement used as src"""
        return None

    def get_controller(
        self, property_name: str
    ) -> Optional[GstPropertyController]:
        """Return the appropriate element controller for the given property"""
        return None

    def get_fader(self, property_name: str):
        controller = self.get_controller(property_name)
        if controller is not None:
            return GstFader(self, property_name)

        return super().get_fader(property_name)

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

    def input_uri(self) -> Union[SessionURI, type(None)]:
        """Return the input uri or None"""
        return None


class GstMediaElements(Collection, HasInstanceProperties):
    def __init__(self):
        super().__init__()
        self.elements = []

    def __getitem__(self, index):
        return self.elements[index]

    def __len__(self):
        return len(self.elements)

    def __contains__(self, item):
        return item in self.elements

    def __iter__(self):
        return iter(self.elements)

    def append(self, element):
        """
        :type element: lisp.backend.media_element.MediaElement
        """
        self.elements.append(element)

        # Add a property for the new added element
        element_name = typename(element)
        setattr(self, element_name, InstanceProperty(default=None))
        setattr(self, element_name, element)

    def remove(self, element):
        self.pop(self.elements.index(element))

    def pop(self, index):
        if index > 0:
            self.elements[index - 1].unlink(self.elements[index])
        if index < len(self.elements) - 1:
            self.elements[index].unlink(self.elements[index + 1])
            self.elements[index - 1].link(self.elements[index + 1])

        element = self.elements.pop(index)
        element.dispose()

        # Remove the element corresponding property
        delattr(self, typename(element))

    def clear(self):
        while self.elements:
            self.pop(len(self.elements) - 1)
