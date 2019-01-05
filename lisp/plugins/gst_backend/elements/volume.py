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

from PyQt5.QtCore import QT_TRANSLATE_NOOP

from lisp.backend.media_element import ElementType, MediaType
from lisp.plugins.gst_backend.gi_repository import Gst
from lisp.plugins.gst_backend.gst_element import (
    GstMediaElement,
    GstProperty,
    GstLiveProperty,
)


class Volume(GstMediaElement):
    ElementType = ElementType.Plugin
    MediaType = MediaType.Audio
    Name = QT_TRANSLATE_NOOP("MediaElementName", "Volume")

    mute = GstProperty("gst_volume", "mute", default=False)
    volume = GstProperty("gst_volume", "volume", default=1.0)
    normal_volume = GstProperty("gst_normal_volume", "volume", default=1.0)

    live_volume = GstLiveProperty(
        "gst_volume", "volume", type=float, range=(0, 10)
    )

    def __init__(self, pipeline):
        super().__init__(pipeline)

        self.gst_volume = Gst.ElementFactory.make("volume", None)
        self.gst_normal_volume = Gst.ElementFactory.make("volume", None)
        self.audio_convert = Gst.ElementFactory.make("audioconvert", None)

        self.pipeline.add(self.gst_normal_volume)
        self.pipeline.add(self.gst_volume)
        self.pipeline.add(self.audio_convert)

        self.gst_volume.link(self.gst_normal_volume)
        self.gst_normal_volume.link(self.audio_convert)

    def sink(self):
        return self.gst_volume

    def src(self):
        return self.audio_convert

    def stop(self):
        self.live_volume = self.volume

    def interrupt(self):
        self.stop()
