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
from lisp.core.properties import Property
from lisp.plugins.gst_backend.gi_repository import Gst
from lisp.plugins.gst_backend.gst_element import GstMediaElement


class UserElement(GstMediaElement):
    ElementType = ElementType.Plugin
    MediaType = MediaType.Audio
    Name = QT_TRANSLATE_NOOP("MediaElementName", "Custom Element")

    bin = Property(default="")

    def __init__(self, pipeline):
        super().__init__(pipeline)

        self.pipeline = pipeline
        self.audio_convert_sink = Gst.ElementFactory.make("audioconvert", None)
        # A default assignment for the bin
        self.gst_bin = Gst.ElementFactory.make("identity", None)
        self.gst_bin.set_property("signal-handoffs", False)
        self.audio_convert_src = Gst.ElementFactory.make("audioconvert", None)

        self.pipeline.add(self.audio_convert_sink)
        self.pipeline.add(self.gst_bin)
        self.pipeline.add(self.audio_convert_src)

        self.audio_convert_sink.link(self.gst_bin)
        self.gst_bin.link(self.audio_convert_src)

        self._old_bin = self.gst_bin
        self.changed("bin").connect(self.__prepare_bin)

    def sink(self):
        return self.audio_convert_sink

    def src(self):
        return self.audio_convert_src

    def __prepare_bin(self, value):
        if value != "" and value != self._old_bin:
            self._old_bin = value

            # If in playing we need to restart the pipeline after unblocking
            playing = self.gst_bin.current_state == Gst.State.PLAYING
            # Block the stream
            pad = self.audio_convert_sink.sinkpads[0]
            probe = pad.add_probe(Gst.PadProbeType.BLOCK, lambda *a: 0, "")

            # Unlink the components
            self.audio_convert_sink.unlink(self.gst_bin)
            self.gst_bin.unlink(self.audio_convert_src)
            self.pipeline.remove(self.gst_bin)

            # Create the bin, when fail use a do-nothing element
            try:
                self.gst_bin = Gst.parse_bin_from_description(value, True)
            except Exception:
                self.gst_bin = Gst.ElementFactory.make("identity", None)
                self.gst_bin.set_property("signal-handoffs", False)

            # Link the components
            self.pipeline.add(self.gst_bin)
            self.audio_convert_sink.link(self.gst_bin)
            self.gst_bin.link(self.audio_convert_src)

            # Unblock the stream
            pad.remove_probe(probe)
            if playing:
                self.pipeline.set_state(Gst.State.PLAYING)
