# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
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
from lisp.ui import elogging
from lisp.modules.timecode.timecode_backend import TimecodeBackend
from lisp.modules.timecode.timecode_common import TcFormat
from lisp.modules.midi.midi_output import MIDIOutput


class Midi(TimecodeBackend):
    Name = 'MIDI'

    __format__ = {
        TcFormat.FILM: 0,
        TcFormat.EBU: 1,
        TcFormat.SMPTE: 3
    }

    __table__ = [
        lambda h, m, s, f, r: f & 15,
        lambda h, m, s, f, r: (f >> 4) & 1,
        lambda h, m, s, f, r: s & 15,
        lambda h, m, s, f, r: (s >> 4) & 3,
        lambda h, m, s, f, r: m & 15,
        lambda h, m, s, f, r: (m >> 4) & 3,
        lambda h, m, s, f, r: h & 15,
        lambda h, m, s, f, r: (h >> 4 & 1) + (r << 1)
    ]

    def __init__(self):
        super().__init__()
        self.__last_time = -1
        self.__last_frame = -1
        if not MIDIOutput().is_open():
            MIDIOutput().open()

    def status(self):
        return MIDIOutput().is_open()

    def __send_fullframe(self, fmt, hours, minutes, seconds, frames):
        """sends fullframe timecode message, in case timecode is non continous (repositioning, rewind)"""
        fmt = self.__format__[fmt]
        hh = (fmt << 5) + hours
        msg = Message('sysex', data=[0x7f, 0x7f, 0x01, 0x01, hh, minutes, seconds, frames])
        MIDIOutput().send(msg)
        self.__last_frame = -1
        return True

    def __send_quarterframe(self, frame_type, fmt, hours, minutes, seconds, frames):
        """send quarterframe midi message"""
        rate = self.__format__[fmt]
        msg = Message('quarter_frame')
        msg.frame_type = frame_type
        msg.frame_value = self.__table__[frame_type](hours, minutes, seconds, frames, rate)
        MIDIOutput().send(msg)

    def __next_frame(self, fmt, time):
        return time - self.__last_time > (fmt.value / 4)

    def send(self, fmt, time, track=-1, rewind=False):
        # TODO: drop handling
        if not self.__next_frame(fmt, time):
            return True

        tt = time_tuple(time)

        hours = int(tt[0])
        if track > 0:
            hours = track

        tick = fmt.value / 4

        frame_type = self.__last_frame

        while self.__last_time + tick < time:
            self.__last_time += tick
            tt_diff = time_tuple(self.__last_time)
            if frame_type < len(self.__table__) - 1:
                frame_type += 1
            else:
                frame_type = 0
            self.__send_quarterframe(frame_type, fmt, hours, int(tt_diff[1]), int(tt_diff[2]), int(tt_diff[3]/fmt.value))
        self.__last_frame = frame_type

        return True

    def stop(self, rclient=False):
        self.__last_time = -1
        self.__last_frame = -1
