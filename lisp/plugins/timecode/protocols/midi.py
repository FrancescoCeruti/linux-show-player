# This file is part of Linux Show Player
#
# Copyright 2017 Francesco Ceruti <ceppofrancy@gmail.com>
# Copyright 2016-2017 Thomas Achtner <info@offtools.de>
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

from mido import Message

from lisp.core.util import time_tuple
from lisp.plugins import get_plugin
from lisp.plugins.timecode.cue_tracker import TcFormat
from lisp.plugins.timecode.protocol import TimecodeProtocol

MIDI_FORMATS = {TcFormat.FILM: 0, TcFormat.EBU: 1, TcFormat.SMPTE: 3}


FRAME_VALUES = [
    lambda h, m, s, f, r: f & 15,
    lambda h, m, s, f, r: (f >> 4) & 1,
    lambda h, m, s, f, r: s & 15,
    lambda h, m, s, f, r: (s >> 4) & 3,
    lambda h, m, s, f, r: m & 15,
    lambda h, m, s, f, r: (m >> 4) & 3,
    lambda h, m, s, f, r: h & 15,
    lambda h, m, s, f, r: (h >> 4 & 1) + (r << 1),
]


class Midi(TimecodeProtocol):
    Name = "MIDI"

    def __init__(self):
        super().__init__()
        self.__last_time = -1
        self.__last_frame = -1
        self.__midi = get_plugin("Midi")

    def __send_full(self, fmt, hours, minutes, seconds, frame):
        """Sends fullframe timecode message.
        
        Used in case timecode is non continuous (repositioning, rewind).
        """
        message = Message(
            "sysex",
            data=[
                0x7F,
                0x7F,
                0x01,
                0x01,
                (MIDI_FORMATS[fmt] << 5) + hours,
                minutes,
                seconds,
                frame,
            ],
        )

        if self.__midi is not None:
            self.__midi.output.send(message)

    def __send_quarter(self, frame_type, fmt, hours, minutes, seconds, frame):
        """Send quarterframe midi message."""
        messsage = Message("quarter_frame")
        messsage.frame_type = frame_type
        messsage.frame_value = FRAME_VALUES[frame_type](
            hours, minutes, seconds, frame, MIDI_FORMATS[fmt]
        )

        if self.__midi is not None:
            self.__midi.send(messsage)

    def send(self, format, time, track=-1):
        # Split the time in its components
        hours, minutes, seconds, millis = time_tuple(time)
        frame = int(millis / format.value)
        if track > -1:
            hours = track

        tick = format.value / 4
        t_diff = time - self.__last_time

        if self.__last_time < 0 or t_diff > tick * 8 or t_diff < 0:
            # First frame or time jumped forward/backward
            self.__send_full(format, hours, minutes, seconds, frame)

            self.__last_frame = 3 if frame % 2 else -1
            self.__last_time = time
        elif t_diff > tick:
            # Send quarter-frames
            frame_type = self.__last_frame
            while self.__last_time + tick < time:
                self.__last_time += tick

                if frame_type < len(FRAME_VALUES) - 1:
                    frame_type += 1
                else:
                    frame_type = 0

                self.__send_quarter(
                    frame_type, format, hours, minutes, seconds, frame
                )

            self.__last_frame = frame_type

        return True

    def finalize(self):
        self.__last_time = -1
        self.__last_frame = -1
