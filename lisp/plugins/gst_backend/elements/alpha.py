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

        # Create elements
        self.sync_element = Gst.ElementFactory.make("identity", None)
        self.gst_alpha = Gst.ElementFactory.make("alpha", None)
        self.gst_background = Gst.ElementFactory.make("videotestsrc", None)
        self.background_scale = Gst.ElementFactory.make("videoscale", None)
        self.background_format = Gst.ElementFactory.make("capsfilter", None)
        self.background_convert = Gst.ElementFactory.make("videoconvert", None)
        self.gst_mixer = Gst.ElementFactory.make("videomixer", "alphamixer")
        self.video_convert = Gst.ElementFactory.make("videoconvert", None)

        # Set properties
        self.gst_background.set_property("pattern", 2)  # Black pattern
        self.gst_alpha.set_property("alpha", 1.0)
        self.gst_alpha.set_property("method", "set")

        self.alpha_controller = GstPropertyController(self.pipeline, self.gst_alpha, self.sync_element, "alpha")

        # Add elements to pipeline
        self.pipeline.add(self.sync_element)
        self.pipeline.add(self.gst_alpha)
        self.pipeline.add(self.gst_mixer)
        self.pipeline.add(self.video_convert)

        self.pipeline.add(self.gst_background)
        self.pipeline.add(self.background_scale)
        self.pipeline.add(self.background_format)
        self.pipeline.add(self.background_convert)

        # Link elements
        self.sync_element.link(self.gst_alpha)
        mixer_pad = self.gst_mixer.get_request_pad("sink_0")
        mixer_pad.set_property("zorder", 1)
        self.gst_alpha.get_static_pad("src").link(mixer_pad)
        self.gst_mixer.link(self.video_convert)

        self.gst_background.link(self.background_scale)
        self.background_scale.link(self.background_format)
        self.background_format.link(self.background_convert)

        self.__block_id = self.background_convert.get_static_pad("src").add_probe(
            Gst.PadProbeType.BLOCK_DOWNSTREAM, lambda *_: Gst.PadProbeReturn.OK
        )

        self.__set_caps = False
        self.__set_probe = False

        pipeline.children[-1].connect("pad-added", self._on_pad_added)
        pipeline.children[-1].connect("source-setup", self.__source_setup)

    def __source_setup(self, source, udata):
        duration = gst_uri_frames(SessionURI(udata.get_uri()))
        self.gst_background.set_property("num-buffers", duration)

    def _on_caps_probe(self, pad, info, *args):
        if self.__set_probe:
            return Gst.PadProbeReturn.OK
        event = info.get_event()
        if not event or event.type != Gst.EventType.CAPS:
            return Gst.PadProbeReturn.OK

        self.__set_probe = True

        caps = event.parse_caps()

        # Apply caps to background_format
        self.background_format.set_property("caps", caps)

        # Now that caps are set, link gst_alpha → mixer
        mixer_pad = self.gst_mixer.get_request_pad("sink_1")
        mixer_pad.set_property("zorder", 0)
        self.background_convert.get_static_pad("src").link(mixer_pad)

        # Remove the blocking probe so background can flow
        if self.__block_id is not None:
            self.background_convert.get_static_pad("src").remove_probe(self.__block_id)
            self.__block_id = None

        # Remove this caps probe and allow normal flow
        pad.remove_probe(self.__probe_handler)
        return Gst.PadProbeReturn.DROP

    def _on_pad_added(self, decodebin, pad):
        if self.__set_caps:
            return
        caps = pad.get_current_caps()
        if not caps:
            return
        struct = caps.get_structure(0)
        if not struct:
            return
        if not struct.has_field("width") or not struct.has_field("height"):
            return
        self.__set_caps = True
        self.__probe_handler = pad.add_probe(Gst.PadProbeType.EVENT_DOWNSTREAM, self._on_caps_probe)

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
        self.pipeline.remove(self.gst_alpha)
        self.pipeline.remove(self.gst_mixer)
        self.pipeline.remove(self.video_convert)

        self.pipeline.remove(self.gst_background)
        self.pipeline.remove(self.background_scale)
        self.pipeline.remove(self.background_format)
        self.pipeline.remove(self.background_convert)
