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
from lisp.plugins.gst_backend.gst_element import GstMediaElement, GstProperty


class AlsaSink(GstMediaElement):
    ElementType = ElementType.Output
    MediaType = MediaType.Audio
    Name = QT_TRANSLATE_NOOP("MediaElementName", "ALSA Out")

    device = GstProperty("alsa_sink", "device", default="")

    def __init__(self, pipeline):
        super().__init__(pipeline)

        self.audio_resample = Gst.ElementFactory.make("audioresample", None)
        self.alsa_sink = Gst.ElementFactory.make("alsasink", "sink")

        self.pipeline.add(self.audio_resample)
        self.pipeline.add(self.alsa_sink)

        self.audio_resample.link(self.alsa_sink)

        self.changed("device").connect(self._update_device)

    def sink(self):
        return self.audio_resample

    def _update_device(self, new_device):
        # Remove and dispose element
        self.audio_resample.unlink(self.alsa_sink)
        self.pipeline.remove(self.alsa_sink)
        self.alsa_sink.set_state(Gst.State.NULL)

        # Create new element and add it to the pipeline
        self.alsa_sink = Gst.ElementFactory.make("alsasink", "sink")
        self.alsa_sink.set_property("device", new_device)

        self.pipeline.add(self.alsa_sink)
        self.audio_resample.link(self.alsa_sink)
