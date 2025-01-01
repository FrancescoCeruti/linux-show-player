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

class AudioEcho(GstMediaElement):
    ElementType = ElementType.Plugin
    MediaType = MediaType.Audio
    Name = QT_TRANSLATE_NOOP("MediaElementName", "Echo/Delay")

    delay     = GstProperty("audioecho", "delay", default=300*1e6)
    feedback  = GstProperty("audioecho", "feedback", default=0.2)
    intensity = GstProperty("audioecho", "intensity", default=0.4)
    max_delay = GstProperty("audioecho", "max-delay", default=5*1e9)

    def __init__(self, pipeline):
        super().__init__(pipeline)

        self.audioecho = Gst.ElementFactory.make("audioecho", "audioecho")
        self.audio_convert = Gst.ElementFactory.make("audioconvert", None)
        self.queue = Gst.ElementFactory.make("queue", None)

        self.pipeline.add(self.audioecho)
        self.pipeline.add(self.audio_convert)
        self.pipeline.add(self.queue)

        self.audioecho.link(self.audio_convert)
        self.audio_convert.link(self.queue)
        

    def sink(self):
        return self.audioecho

    def src(self):
        return self.queue
