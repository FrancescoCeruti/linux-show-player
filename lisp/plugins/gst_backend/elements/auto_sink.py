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


class AVSinkBin(Gst.Bin):
    def __init__(self):
        super().__init__()

        # Audio path
        self.audio_queue = Gst.ElementFactory.make("queue", None)
        self.audio_convert = Gst.ElementFactory.make("audioconvert", None)
        # Video path
        self.video_queue = Gst.ElementFactory.make("queue", None)
        self.video_convert = Gst.ElementFactory.make("videoconvert", None)

        for el in [
            self.audio_queue,
            self.audio_convert,
            self.video_queue,
            self.video_convert,
        ]:
            self.add(el)

        # Link both paths
        self.audio_queue.link(self.audio_convert)
        self.video_queue.link(self.video_convert)

        # Input pads (ghost pads)
        self.add_pad(Gst.GhostPad.new("audio_sink", self.audio_queue.get_static_pad("sink")))
        self.add_pad(Gst.GhostPad.new("video_sink", self.video_queue.get_static_pad("sink")))

        # Output pads (ghost pads)
        self.add_pad(Gst.GhostPad.new("audio_src", self.audio_convert.get_static_pad("src")))
        self.add_pad(Gst.GhostPad.new("video_src", self.video_convert.get_static_pad("src")))

    def remove_audio(self):
        if self.get_static_pad("audio_sink"):
            self.remove_pad(self.get_static_pad("audio_sink"))
        if self.get_static_pad("audio_src"):
            self.remove_pad(self.get_static_pad("audio_src"))

    def remove_video(self):
        if self.get_static_pad("video_sink"):
            self.remove_pad(self.get_static_pad("video_sink"))
        if self.get_static_pad("video_src"):
            self.remove_pad(self.get_static_pad("video_src"))


class AutoSink(GstMediaElement):
    ElementType = ElementType.Output
    MediaType = MediaType.AudioAndVideo
    Name = QT_TRANSLATE_NOOP("MediaElementName", "System Out")

    def __init__(self, pipeline):
        super().__init__(pipeline)

        self.avbin = AVSinkBin()
        self.audio_sink = Gst.ElementFactory.make("autoaudiosink", None)
        self.video_sink = Gst.ElementFactory.make("autovideosink", None)

        self.pipeline.add(self.avbin)
        self.pipeline.add(self.audio_sink)
        self.pipeline.add(self.video_sink)

        self.avbin.link(self.audio_sink)
        self.avbin.link(self.video_sink)

    def sink(self):
        return self.avbin

    def remove_audio(self):
        self.avbin.unlink(self.audio_sink)
        self.pipeline.remove(self.audio_sink)
        self.avbin.remove_audio()

    def remove_video(self):
        self.avbin.unlink(self.video_sink)
        self.pipeline.remove(self.video_sink)
        self.avbin.remove_video()

    def stop(self):
        self.video_sink.set_state(Gst.State.NULL)
