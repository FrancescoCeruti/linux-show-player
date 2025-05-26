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

import socket
import struct
import logging

from lisp.core.util import time_tuple
from lisp.plugins.timecode.cue_tracker import TcFormat
from lisp.plugins.timecode.protocol import TimecodeProtocol
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)


class Artnet(TimecodeProtocol):
    Name = "ArtNet"

    def __init__(self):
        super().__init__()

        self.__sender = ArtNetTimecodeSender()

    def send(self, fmt, time, track=-1):
        hours, minutes, seconds, millis = time_tuple(time)
        frame = int(millis / fmt.value)
        if track > -1:
            hours = track

        try:
            self.__sender.send_timecode(fmt, hours, minutes, seconds, frame)
        except Exception:
            logger.exception(
                translate("TimecodeError", "Cannot send timecode.")
            )
            return False

        return True

    def finalize(self):
        self.__sender.close()


class ArtNetTimecodeSender:
    HEADER = b"Art-Net\x00"
    OP_CODE = 0x9700
    FORMAT_CODES = {
        TcFormat.FILM: 0x00,
        TcFormat.EBU: 0x01,
        # TcFormat.DF: 0x02,
        TcFormat.SMPTE: 0x03,
    }

    def __init__(self, target_ip="255.255.255.255", port=6454):
        self.target_ip = target_ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def build_packet(self, fmt, hours, minutes, seconds, frames):
        packet = bytearray()
        packet.extend(self.HEADER)
        packet.extend(struct.pack("<H", self.OP_CODE))
        packet.append(0)  # ProtVerHi
        packet.append(14)  # ProtVerLo
        packet.append(0)  # Filler1
        packet.append(0)  # StreamId
        packet.append(frames)  # Frames
        packet.append(seconds)  # Seconds
        packet.append(minutes)  # Minutes
        packet.append(hours)  # Hours
        packet.append(self.FORMAT_CODES[fmt])  # Type

        return packet

    def send_timecode(self, fmt, hours, minutes, seconds, frames):
        self.sock.sendto(
            self.build_packet(fmt, hours, minutes, seconds, frames),
            (self.target_ip, self.port),
        )

    def close(self):
        self.sock.close()
