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
from lisp.core.signal import Signal
from lisp.plugins.gst_backend.gi_repository import Gst
from lisp.plugins.gst_backend.gst_element import GstMediaElement, GstProperty


class DbMeter(GstMediaElement):
    ElementType = ElementType.Plugin
    MediaType = MediaType.Audio
    Name = QT_TRANSLATE_NOOP("MediaElementName", "dB Meter")

    interval = GstProperty("level", "interval", default=50 * Gst.MSECOND)
    peak_ttl = GstProperty("level", "peak-ttl", default=Gst.SECOND)
    peak_falloff = GstProperty("level", "peak-falloff", default=20)

    def __init__(self, pipeline):
        super().__init__(pipeline)
        self.level_ready = Signal()

        self.pipeline = pipeline
        self.level = Gst.ElementFactory.make("level", None)
        self.level.set_property("post-messages", True)
        self.level.set_property("interval", 50 * Gst.MSECOND)
        self.level.set_property("peak-ttl", Gst.SECOND)
        self.level.set_property("peak-falloff", 20)
        self.audio_convert = Gst.ElementFactory.make("audioconvert", None)

        self.pipeline.add(self.level)
        self.pipeline.add(self.audio_convert)

        self.level.link(self.audio_convert)

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        self._handler = bus.connect("message::element", self.__on_message)

    def dispose(self):
        bus = self.pipeline.get_bus()
        bus.remove_signal_watch()
        bus.disconnect(self._handler)

    def sink(self):
        return self.level

    def src(self):
        return self.audio_convert

    def __on_message(self, bus, message):
        if message.src == self.level:
            structure = message.get_structure()
            if structure is not None and structure.has_name("level"):
                self.level_ready.emit(
                    structure.get_value("peak"),
                    structure.get_value("rms"),
                    structure.get_value("decay"),
                )
