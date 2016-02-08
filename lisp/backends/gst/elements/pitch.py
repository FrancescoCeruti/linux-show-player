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

from lisp.backends.base.media_element import ElementType, MediaType
from lisp.backends.gst.gi_repository import Gst
from lisp.backends.gst.gst_element import GstMediaElement, GstProperty


class Pitch(GstMediaElement):
    ElementType = ElementType.Plugin
    MediaType = MediaType.Audio
    Name = "Pitch"

    pitch = GstProperty('pitch', default=1.0)

    def __init__(self, pipe):
        super().__init__()

        self.pitch = Gst.ElementFactory.make("pitch", None)
        self.audio_converter = Gst.ElementFactory.make("audioconvert", None)

        pipe.add(self.pitch)
        pipe.add(self.audio_converter)

        self.pitch.link(self.audio_converter)

    def sink(self):
        return self.pitch

    def src(self):
        return self.audio_converter
