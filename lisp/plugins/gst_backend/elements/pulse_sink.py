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


class PulseSink(GstMediaElement):
    ElementType = ElementType.Output
    MediaType = MediaType.Audio
    Name = QT_TRANSLATE_NOOP("MediaElementName", "PulseAudio Out")

    def __init__(self, pipeline):
        super().__init__(pipeline)

        self.pulse_sink = Gst.ElementFactory.make("pulsesink", "sink")
        self.pulse_sink.set_property("client-name", "Linux Show Player")

        self.pipeline.add(self.pulse_sink)

    def sink(self):
        return self.pulse_sink
