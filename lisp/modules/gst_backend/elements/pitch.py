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

from PyQt5.QtCore import QT_TRANSLATE_NOOP

from lisp.backend.media_element import ElementType, MediaType
from lisp.modules.gst_backend.gi_repository import Gst
from lisp.modules.gst_backend.gst_element import GstMediaElement, GstProperty


class Pitch(GstMediaElement):
    ElementType = ElementType.Plugin
    MediaType = MediaType.Audio
    Name = QT_TRANSLATE_NOOP('MediaElementName', 'Pitch')

    pitch = GstProperty('gst_pitch', gst_name='pitch', default=1.0)

    def __init__(self, pipe):
        super().__init__()

        self.gst_pitch = Gst.ElementFactory.make('pitch', None)
        self.audio_converter = Gst.ElementFactory.make('audioconvert', None)

        pipe.add(self.gst_pitch)
        pipe.add(self.audio_converter)

        self.gst_pitch.link(self.audio_converter)

    def sink(self):
        return self.gst_pitch

    def src(self):
        return self.audio_converter
