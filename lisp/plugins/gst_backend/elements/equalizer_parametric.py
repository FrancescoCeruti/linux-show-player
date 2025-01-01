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
from lisp.plugins.gst_backend.gst_element import GstMediaElement
from lisp.plugins.gst_backend.gst_properties import GstChildProperty, GstProperty


class EqualizerParametric(GstMediaElement):
    ElementType = ElementType.Plugin
    MediaType = MediaType.Audio
    Name = QT_TRANSLATE_NOOP("MediaElementName", "Parametric Equalizer")
    
    bands = []

    # gain0 = GstProperty("equalizer", "gain0", default=0)
    # gain1 = GstProperty("equalizer", "gain1", default=0)
    # gain2 = GstProperty("equalizer", "gain2", default=0)
    # gain3 = GstProperty("equalizer", "gain3", default=0)
    # gain4 = GstProperty("equalizer", "gain4", default=0)
    # freq0 = GstProperty("equalizer", "freq0", default=0)
    # freq1 = GstProperty("equalizer", "freq1", default=0)
    # freq2 = GstProperty("equalizer", "freq2", default=0)
    # freq3 = GstProperty("equalizer", "freq3", default=0)
    # freq4 = GstProperty("equalizer", "freq4", default=0)
    # bandwidth0 = GstProperty("equalizer", "bandwidth0", default=0)
    # bandwidth1 = GstProperty("equalizer", "bandwidth1", default=0)
    # bandwidth2 = GstProperty("equalizer", "bandwidth2", default=0)
    # bandwidth3 = GstProperty("equalizer", "bandwidth3", default=0)
    # bandwidth4 = GstProperty("equalizer", "bandwidth4", default=0)
    # band0 = GstProperty("equalizer", "band1", default={'gain': -6, 'freq': 100, 'bandwidth': 0.3})
    # band1 = GstProperty("equalizer", "band-1", default={'gain': 0, 'freq': 250, 'bandwidth': 0.3})
    # band2 = GstProperty("equalizer", "band-2", default={'gain': 0, 'freq': 600, 'bandwidth': 0.3})
    # band3 = GstProperty("equalizer", "band-3", default={'gain': 8, 'freq': 1250, 'bandwidth': 0.3})
    # band4 = GstProperty("equalizer", "band-4", default={'gain': 0, 'freq': 10000, 'bandwidth': 0.3})
    
    band0 = GstChildProperty("equalizer", "band0", default={'gain': 9, 'freq': 1000, 'bandwidth': 5})

    num_bands  = GstProperty("equalizer", "num-bands", default=5)

   
    def __init__(self, pipeline):
        super().__init__(pipeline)

        self.equalizer = Gst.ElementFactory.make("equalizer-nbands", "equalizer")
        self.audio_converter = Gst.ElementFactory.make("audioconvert", None)

        self.pipeline.add(self.equalizer)
        self.pipeline.add(self.audio_converter)

        self.equalizer.link(self.audio_converter)

    def addBand(self, band):
        pass
    def removeBand(self, band):
        pass
    
    def sink(self):
        return self.equalizer

    def src(self):
        return self.audio_converter
