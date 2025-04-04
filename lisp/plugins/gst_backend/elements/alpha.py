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
from lisp.plugins.gst_backend.gst_utils import gst_uri_frames
from lisp.core.session_uri import SessionURI


class Alpha(GstMediaElement):
    ElementType = ElementType.Plugin
    MediaType = MediaType.Video
    Name = QT_TRANSLATE_NOOP("MediaElementName", "Alpha")

    FadeInterpolationMode = GstController.InterpolationMode.CUBIC_MONOTONIC

    alpha = GstProperty("gst_alpha", "alpha", default=1.0)

    live_alpha = GstLiveProperty("gst_alpha", "alpha", type=float, range=(0, 1))

    def __init__(self, pipeline):
        super().__init__(pipeline)

        pipeline.children[-1].connect("pad-added", self._on_pad_added)
        pipeline.children[-1].connect("source-setup", self.__source_setup)

        # Create elements
        self.sync_element = Gst.ElementFactory.make("identity", None)
        self.gst_black = Gst.ElementFactory.make("videotestsrc", None)
        self.black_scale = Gst.ElementFactory.make("videoscale", None)
        self.black_format = Gst.ElementFactory.make("capsfilter", None)
        self.gst_alpha = Gst.ElementFactory.make("alpha", None)
        self.gst_mixer = Gst.ElementFactory.make("videomixer", "alphamixer")
        self.video_convert = Gst.ElementFactory.make("videoconvert", None)

        # Set properties
        self.gst_black.set_property("pattern", 2)  # Black pattern
        self.gst_alpha.set_property("alpha", 1.0)

        self.alpha_controller = GstPropertyController(self.pipeline, self.gst_alpha, self.sync_element, "alpha")

        # Add elements to pipeline
        self.pipeline.add(self.sync_element)
        self.pipeline.add(self.gst_alpha)
        self.pipeline.add(self.gst_mixer)
        self.pipeline.add(self.video_convert)

    def __source_setup(self, source, udata):
        duration = gst_uri_frames(SessionURI(udata.get_uri()))
        self.gst_black.set_property("num-buffers", duration)

        # Add elements to pipeline
        self.pipeline.add(self.gst_black)
        self.pipeline.add(self.black_scale)
        self.pipeline.add(self.black_format)

        # Link elements
        self.gst_black.link(self.black_scale)
        self.black_scale.link(self.black_format)
        self.black_format.link(self.gst_mixer)
        self.sync_element.link(self.gst_alpha)
        self.gst_alpha.link(self.gst_mixer)
        self.gst_mixer.link(self.video_convert)

    def _on_pad_added(self, decodebin, pad):
        caps = pad.get_current_caps()
        if caps:
            self.black_format.set_property("caps", caps)

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
        self.live_volume = self.alpha
