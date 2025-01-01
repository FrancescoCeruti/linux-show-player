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

from enum import Enum
from PyQt5.QtCore import QT_TRANSLATE_NOOP

from lisp.backend.media_element import ElementType, MediaType
from lisp.plugins.gst_backend.gi_repository import Gst
from lisp.plugins.gst_backend.gst_element import GstMediaElement
from lisp.plugins.gst_backend.gst_properties import GstProperty

class BandpassFilter(GstMediaElement):
    ElementType = ElementType.Plugin
    MediaType = MediaType.Audio
    Name = QT_TRANSLATE_NOOP("MediaElementName", "Bandpass filter")

    class Window(Enum):
        Hamming = 0
        Blackman = 1
        Gaussian = 2
        Cosine = 3
        Hann = 4

    class WindowMode(Enum):
        BandPass = 0
        BandReject = 1

    loFreq = GstProperty("bandpass", "lower-frequency", default=1)
    hiFreq = GstProperty("bandpass", "upper-frequency", default=20000)
    mode   = GstProperty("bandpass", "mode", default=WindowMode.BandPass)
    window = GstProperty("bandpass", "window", default=Window.Hamming)
    length = GstProperty("bandpass", "length", default=101)

    def __init__(self, pipeline):
        super().__init__(pipeline)

        self.bandpass = Gst.ElementFactory.make("audiowsincband", None)
        self.audio_converter = Gst.ElementFactory.make("audioconvert", None)

        self.pipeline.add(self.bandpass)
        self.pipeline.add(self.audio_converter)

        self.bandpass.link(self.audio_converter)


    def sink(self):
        return self.bandpass

    def src(self):
        return self.audio_converter
