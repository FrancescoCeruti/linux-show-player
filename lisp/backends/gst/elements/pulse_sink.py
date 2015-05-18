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


class PulseSink(GstMediaElement):
    ElementType = ElementType.Output
    MediaType = MediaType.Audio
    Name = 'PulseAudioSink'

    _properties_ = ('server', 'device', 'client_name', 'volume', 'mute')

    def __init__(self, pipe):
        super().__init__()

        self._sink = Gst.ElementFactory.make('pulsesink', 'sink')
        self._sink.set_property('client-name', 'Linux Show Player')
        pipe.add(self._sink)

        self.server = None
        self.device = None
        self.client_name = 'Linux Show Player'
        self.volume = 1.0
        self.mute = False

        self.property_changed.connect(self.__property_changed)

    def sink(self):
        return self._sink

    def __property_changed(self, name, value):
        name.replace('_', '-')
        self._sink.set_property(name, value)
