# This file is part of Linux Show Player
#
# Copyright 2018 Francesco Ceruti <ceppofrancy@gmail.com>
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


class Flip(GstMediaElement):
    ElementType = ElementType.Plugin
    MediaType = MediaType.Video
    Name = QT_TRANSLATE_NOOP("MediaElementName", "Flip")

    class Method(Enum):
        NONE = 0
        CLOCKWISE90 = 1
        ROTATE180 = 2
        COUNTERCLOCKWISE90 = 3
        HORIZONTALFLIP = 4
        VERTICALFLIP = 5
        UPPERLEFTDIAGONAL = 6
        UPPERRIGHTDIAGONAL = 7

    method = GstProperty("gst_videoflip", "method", default=Method.NONE.value)

    def __init__(self, pipeline):
        super().__init__(pipeline)

        # Create elements
        self.sync_element = Gst.ElementFactory.make("identity", "flip-sync")
        self.gst_videoflip = Gst.ElementFactory.make("videoflip", "videoflip")
        self.video_convert = Gst.ElementFactory.make("videoconvert", "flip-convert")

        # Add elements to pipeline
        self.pipeline.add(self.sync_element)
        self.pipeline.add(self.gst_videoflip)
        self.pipeline.add(self.video_convert)

        # Link elements
        self.sync_element.link(self.gst_videoflip)
        self.gst_videoflip.link(self.video_convert)

    def sink(self):
        return self.sync_element

    def src(self):
        return self.video_convert

    def dispose(self):
        self.pipeline.remove(self.sync_element)
        self.pipeline.remove(self.gst_videoflip)
        self.pipeline.remove(self.video_convert)
