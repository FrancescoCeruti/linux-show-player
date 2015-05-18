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


class AudioPan(GstMediaElement):
    ElementType = ElementType.Plugin
    MediaType = MediaType.Audio
    Name = "AudioPan"

    _properties_ = ('pan')

    def __init__(self, pipe):
        super().__init__()

        self._panorama = Gst.ElementFactory.make("audiopanorama", None)
        self._convert = Gst.ElementFactory.make("audioconvert", None)

        pipe.add(self._panorama)
        pipe.add(self._convert)

        self._panorama.link(self._convert)

        self.pan = .0

        self.property_changed.connect(self.__property_changed)

    def sink(self):
        return self._panorama

    def src(self):
        return self._convert

    def __property_changed(self, name, value):
        self._panorama.set_property(name, value)
