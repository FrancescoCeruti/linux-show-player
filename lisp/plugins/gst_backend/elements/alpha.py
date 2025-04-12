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
from typing import Optional

from PyQt5.QtCore import QT_TRANSLATE_NOOP

from lisp.backend.media_element import ElementType, MediaType
from lisp.plugins.gst_backend.gi_repository import Gst, GstController
from lisp.plugins.gst_backend.gst_element import GstMediaElement
from lisp.plugins.gst_backend.gst_properties import (
    GstProperty,
    GstLiveProperty,
    GstPropertyController,
)


class Alpha(GstMediaElement):
    ElementType = ElementType.Plugin
    MediaType = MediaType.Video
    Name = QT_TRANSLATE_NOOP("MediaElementName", "Alpha")

    class Background(Enum):
        CHECKER = 0
        BLACK = 1
        WHITE = 2
        TRANSPARENT = 3

    FadeInterpolationMode = GstController.InterpolationMode.CUBIC_MONOTONIC

    background = GstProperty("gst_compositor", "background", default=Background.BLACK.value)
    alpha = GstProperty("compositor_pad", "alpha", default=1.0)
    live_alpha = GstLiveProperty("compositor_pad", "alpha", type=float, range=(0, 1))

    def __init__(self, pipeline):
        super().__init__(pipeline)

        # Create elements
        self.sync_element = Gst.ElementFactory.make("identity", "alpha-sync")
        self.gst_compositor = Gst.ElementFactory.make("compositor", "alpha-compositor")
        self.video_convert = Gst.ElementFactory.make("videoconvert", "alpha-convert")

        self.compositor_pad = self.gst_compositor.get_request_pad("sink_0")

        self.alpha_controller = GstPropertyController(self.pipeline, self.compositor_pad, self.sync_element, "alpha")

        # Add elements to pipeline
        self.pipeline.add(self.sync_element)
        self.pipeline.add(self.gst_compositor)
        self.pipeline.add(self.video_convert)

        # Link elements
        self.sync_element.get_static_pad("src").link(self.compositor_pad)
        self.gst_compositor.link(self.video_convert)

    def get_controller(self, property_name: str) -> Optional[GstPropertyController]:
        if property_name == "live_alpha":
            return self.alpha_controller
        return None

    def sink(self):
        return self.sync_element

    def src(self):
        return self.video_convert

    def stop(self):
        self.alpha_controller.reset()
        self.live_alpha = self.alpha

    def dispose(self):
        self.pipeline.remove(self.sync_element)
        self.pipeline.remove(self.gst_compositor)
        self.pipeline.remove(self.video_convert)
