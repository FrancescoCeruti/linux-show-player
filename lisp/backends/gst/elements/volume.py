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

from lisp.backends.base.media_element import ElementType, MediaType
from lisp.backends.gst.gst_element import GstMediaElement
from lisp.backends.gst.gi_repository import Gst


class Volume(GstMediaElement):
    ElementType = ElementType.Plugin
    MediaType = MediaType.Audio
    Name = "Volume"

    _properties_ = ('mute', 'volume', 'normal_volume')

    def __init__(self, pipe):
        super().__init__()

        self._volume = Gst.ElementFactory.make("volume", None)
        self._normal = Gst.ElementFactory.make("volume", None)
        self._convert = Gst.ElementFactory.make("audioconvert", None)

        pipe.add(self._normal)
        pipe.add(self._volume)
        pipe.add(self._convert)

        self._volume.link(self._normal)
        self._normal.link(self._convert)

        self.mute = False
        self.volume = 1.0
        self.normal_volume = 1.0

        self.property_changed.connect(self.__property_changed)

    def sink(self):
        return self._volume

    def src(self):
        return self._convert

    def __property_changed(self, name, value):
        if name == "normal_volume":
            self._normal.set_property("volume", value)
        else:
            self._volume.set_property(name, value)
