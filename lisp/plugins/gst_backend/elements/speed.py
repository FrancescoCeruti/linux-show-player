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


class Speed(GstMediaElement):
    ElementType = ElementType.Plugin
    MediaType = MediaType.Audio
    Name = QT_TRANSLATE_NOOP("MediaElementName", "Speed")

    speed = Property(default=1.0)

    def __init__(self, pipeline):
        super().__init__(pipeline)

        self.pipeline = pipeline
        self.scale_tempo = Gst.ElementFactory.make("scaletempo", None)
        self.audio_convert = Gst.ElementFactory.make("audioconvert", None)

        self.pipeline.add(self.scale_tempo)
        self.pipeline.add(self.audio_convert)

        self.scale_tempo.link(self.audio_convert)

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        self._handler = bus.connect("message", self.__on_message)

        self._old_speed = self.speed
        self.changed("speed").connect(self.__prepare_speed)

    def __prepare_speed(self, value):
        if self._old_speed != value:
            self._old_speed = value

            if self.pipeline.current_state == Gst.State.PLAYING:
                self.__change_speed()

    def sink(self):
        return self.scale_tempo

    def src(self):
        return self.audio_convert

    def dispose(self):
        bus = self.pipeline.get_bus()
        bus.remove_signal_watch()
        bus.disconnect(self._handler)

    def __on_message(self, bus, message):
        if (
            message.type == Gst.MessageType.STATE_CHANGED
            and message.src == self.scale_tempo
            and message.parse_state_changed()[1] == Gst.State.PLAYING
        ):
            self.__change_speed()

    def __change_speed(self):
        self.scale_tempo.seek(
            self.speed,
            Gst.Format.TIME,
            Gst.SeekFlags.FLUSH | Gst.SeekFlags.ACCURATE,
            Gst.SeekType.SET,
            self.scale_tempo.query_position(Gst.Format.TIME)[1],
            Gst.SeekType.NONE,
            0,
        )
