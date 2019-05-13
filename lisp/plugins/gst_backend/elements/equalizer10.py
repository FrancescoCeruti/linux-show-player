# This file is part of Linux Show Player
#
# Copyright 2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtCore import QT_TRANSLATE_NOOP

from lisp.backend.media_element import ElementType, MediaType
from lisp.plugins.gst_backend.gi_repository import Gst
from lisp.plugins.gst_backend.gst_element import GstMediaElement, GstProperty


class Equalizer10(GstMediaElement):
    ElementType = ElementType.Plugin
    MediaType = MediaType.Audio
    Name = QT_TRANSLATE_NOOP("MediaElementName", "10 Bands Equalizer")

    band0 = GstProperty("equalizer", "band0", default=0)
    band1 = GstProperty("equalizer", "band1", default=0)
    band2 = GstProperty("equalizer", "band2", default=0)
    band3 = GstProperty("equalizer", "band3", default=0)
    band4 = GstProperty("equalizer", "band4", default=0)
    band5 = GstProperty("equalizer", "band5", default=0)
    band6 = GstProperty("equalizer", "band6", default=0)
    band7 = GstProperty("equalizer", "band7", default=0)
    band8 = GstProperty("equalizer", "band8", default=0)
    band9 = GstProperty("equalizer", "band9", default=0)

    def __init__(self, pipeline):
        super().__init__(pipeline)

        self.equalizer = Gst.ElementFactory.make("equalizer-10bands", None)
        self.audio_converter = Gst.ElementFactory.make("audioconvert", None)

        self.pipeline.add(self.equalizer)
        self.pipeline.add(self.audio_converter)

        self.equalizer.link(self.audio_converter)

    def sink(self):
        return self.equalizer

    def src(self):
        return self.audio_converter
