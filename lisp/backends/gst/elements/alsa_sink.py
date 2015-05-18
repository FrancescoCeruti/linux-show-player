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


class AlsaSink(GstMediaElement):
    ElementType = ElementType.Output
    MediaType = MediaType.Audio
    Name = 'AlsaSink'

    _properties_ = ('device', 'volume', 'mute')

    def __init__(self, pipe):
        super().__init__()

        self._volume = Gst.ElementFactory.make('volume', None)
        self._sink = Gst.ElementFactory.make('alsasink', 'sink')

        pipe.add(self._volume)
        pipe.add(self._sink)

        self._volume.link(self._sink)

        self.device = ''
        self.volume = 1.0
        self.mute = False

        self.property_changed.connect(self.__property_changed)

    def sink(self):
        return self._volume

    def __property_changed(self, name, value):
        if name == 'device':
            self._sink.set_property(name, value)
        else:
            self._volume.set_property(name, value)
