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

from PyQt5.QtCore import QT_TRANSLATE_NOOP

from lisp.backend.media_element import ElementType, MediaType
from lisp.plugins.gst_backend.gi_repository import Gst
from lisp.plugins.gst_backend.gst_element import GstMediaElement
from lisp.plugins.gst_backend.gst_properties import GstProperty


class WaylandSink(GstMediaElement):
    ElementType = ElementType.Output
    MediaType = MediaType.Video
    Name = QT_TRANSLATE_NOOP("MediaElementName", "Wayland Video")

    def __init__(self, pipeline):
        super().__init__(pipeline)
        
        device = GstProperty("wayland_sink", "display", default="wayland-0")
        fullscreen = GstProperty("wayland_sink", "fullscreen", default=True)

        self.wayland_sink = Gst.ElementFactory.make("waylandsink", "wayland_sink")
        # Need to set this explicitly for some reason
        # self.wayland_sink.set_property("fullscreen", fullscreen)
        self.pipeline.add(self.wayland_sink)

    def sink(self):
        return self.wayland_sink
