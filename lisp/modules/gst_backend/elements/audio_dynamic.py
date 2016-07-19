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

from enum import Enum

from PyQt5.QtCore import QT_TRANSLATE_NOOP

from lisp.backend.media_element import ElementType, MediaType
from lisp.modules.gst_backend.gi_repository import Gst
from lisp.modules.gst_backend.gst_element import GstMediaElement, GstProperty


class AudioDynamic(GstMediaElement):
    ElementType = ElementType.Plugin
    MediaType = MediaType.Audio
    Name = QT_TRANSLATE_NOOP('MediaElementName', 'Compressor/Expander')

    class Mode(Enum):
        Compressor = 'compressor'
        Expander = 'expander'


    class Characteristics(Enum):
        HardKnee = 'hard-knee'
        SoftKnee = 'soft-knee'

    mode = GstProperty('audio_dynamic', default=Mode.Compressor.value)
    characteristics = GstProperty('audio_dynamic',
                                 default=Characteristics.HardKnee.value)
    ratio = GstProperty('audio_dynamic', default=1)
    threshold = GstProperty('audio_dynamic', default=0)

    def __init__(self, pipe):
        super().__init__()

        self.audio_dynamic = Gst.ElementFactory.make('audiodynamic', None)
        self.audio_converter = Gst.ElementFactory.make('audioconvert', None)

        pipe.add(self.audio_dynamic)
        pipe.add(self.audio_converter)

        self.audio_dynamic.link(self.audio_converter)

        self.update_properties(self.properties())

    def sink(self):
        return self.audio_dynamic

    def src(self):
        return self.audio_converter