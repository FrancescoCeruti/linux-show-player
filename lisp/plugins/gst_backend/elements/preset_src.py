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

import math

from PyQt5.QtCore import QT_TRANSLATE_NOOP

from lisp.backend.media_element import MediaType
from lisp.core.properties import Property
from lisp.plugins.gst_backend.gi_repository import Gst, GstApp
from lisp.plugins.gst_backend.gst_element import GstSrcElement


class PresetSrc(GstSrcElement):
    MediaType = MediaType.Audio
    Name = QT_TRANSLATE_NOOP("MediaElementName", "Preset Input")

    FREQ = 8000
    SILENCE = lambda t: 0
    PRESETS = {
        "The 42 melody": lambda t: t * (42 & t >> 10),
        "Mission": lambda t: (~t >> 2)
        * ((127 & t * (7 & t >> 10)) < (245 & t * (2 + (5 & t >> 14)))),
        "80's": lambda t: (t << 3)
        * [8 / 9, 1, 9 / 8, 6 / 5, 4 / 3, 3 / 2, 0][
            [0xD2D2C8, 0xCE4088, 0xCA32C8, 0x8E4009][t >> 14 & 3]
            >> (
                0x3DBE4688 >> (18 if (t >> 10 & 15) > 9 else t >> 10 & 15) * 3
                & 7
            )
            * 3
            & 7
        ],
        "Game 1": lambda t: (t * (0xCA98 >> (t >> 9 & 14) & 15) | t >> 8),
        "Game 2": lambda t: t * 5 & (t >> 7)
        | t * 3 & (t * 4 >> 10) - int(math.cos(t >> 3)) * 10
        | t >> 5 & int(math.sin(t >> 4))
        | t >> 4,
        "Club": lambda t: (
            ((t * (t ^ t % 255) | (t >> 4)) >> 1)
            if (t & 4096)
            else (t >> 3) | (t << 2 if (t & 8192) else t)
        )
        + t * (((t >> 9) ^ ((t >> 9) - 1) ^ 1) % 13),
        "Laser 1": lambda t: t * (t >> 5 | t >> 15) & 80 & t * 4 >> 9,
        "Laser 2": lambda t: (t * (t >> 5 | t >> 23) & 43 & t >> 9)
        ^ (t & t >> 20 | t >> 9),
        "Generator": lambda t: (t * (t >> 22 | t >> 3) & 43 & t >> 8)
        ^ (t & t >> 12 | t >> 4),
    }

    preset = Property(default="The 42 melody")

    def __init__(self, pipeline):
        super().__init__(pipeline)
        self.n_sample = 0
        self.caps = (
            "audio/x-raw,format=U8,channels=1,layout=interleaved,"
            "rate=" + str(PresetSrc.FREQ)
        )

        self.app_src = Gst.ElementFactory.make("appsrc", "appsrc")
        self.app_src.set_property("stream-type", GstApp.AppStreamType.SEEKABLE)
        self.app_src.set_property("format", Gst.Format.TIME)
        self.app_src.set_property("caps", Gst.Caps.from_string(self.caps))
        self.app_src.connect("need-data", self.generate_samples)
        self.app_src.connect("seek-data", self.seek)

        self.audio_converter = Gst.ElementFactory.make("audioconvert", None)

        self.pipeline.add(self.app_src)
        self.pipeline.add(self.audio_converter)

        self.app_src.link(self.audio_converter)

    def stop(self):
        self.n_sample = 0

    def interrupt(self):
        self.stop()

    def generate_samples(self, src, need_bytes):
        remaining = int(self.duration / 1000 * PresetSrc.FREQ - self.n_sample)
        if remaining <= 0:
            self.n_sample = 0
            src.emit("end-of-stream")
        else:
            if need_bytes > remaining:
                need_bytes = remaining

            function = PresetSrc.PRESETS.get(self.preset, PresetSrc.SILENCE)
            sample = []
            while len(sample) < need_bytes:
                value = function(self.n_sample)
                sample.append(int(value % 256))
                self.n_sample += 1

            buffer = Gst.Buffer.new_wrapped(bytes(sample))
            src.emit("push-buffer", buffer)

    def seek(self, src, time):
        self.n_sample = int(abs(time / Gst.SECOND) * PresetSrc.FREQ)
        return True

    def src(self):
        return self.audio_converter
