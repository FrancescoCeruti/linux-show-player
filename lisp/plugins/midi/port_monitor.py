# This file is part of Linux Show Player
#
# Copyright 2019 Francesco Ceruti <ceppofrancy@gmail.com>
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

import logging
from threading import Thread
from time import sleep

try:
    from pyalsa import alsaseq
except ImportError:
    alsaseq = False

from lisp.core.signal import Signal
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)


class PortMonitor:
    ClientName = "LinuxShowPlayer_Monitor"

    def __init__(self):
        self.port_removed = Signal()
        self.port_added = Signal()


class _ALSAPortMonitor(PortMonitor):
    SEQ_OPEN_INPUT = 2
    SEQ_OPEN_OUTPUT = 1
    SEQ_OPEN_DUPLEX = SEQ_OPEN_OUTPUT | SEQ_OPEN_INPUT
    SEQ_BLOCK = 0
    SEQ_NONBLOCK = 1
    SEQ_CLIENT_SYSTEM = 0

    SEQ_PORT_SYSTEM_ANNOUNCE = 1
    SEQ_PORT_CAP_READ = 1
    SEQ_PORT_CAP_WRITE = 2
    SEQ_PORT_CAP_RW = SEQ_PORT_CAP_READ | SEQ_PORT_CAP_WRITE
    PORT_TYPE_APPLICATION = 1048576

    def __init__(self):
        super().__init__()
        self.__thread = Thread(target=self.__loop, daemon=True)

        try:
            # Create ALSA Sequencer
            self.__seq = alsaseq.Sequencer(
                name="default",
                clientname=_ALSAPortMonitor.ClientName,
                streams=_ALSAPortMonitor.SEQ_OPEN_DUPLEX,
                mode=_ALSAPortMonitor.SEQ_NONBLOCK,
            )

            # Create monitor port
            self.__port = self.__seq.create_simple_port(
                name="monitor",
                type=_ALSAPortMonitor.PORT_TYPE_APPLICATION,
                caps=_ALSAPortMonitor.SEQ_PORT_CAP_RW,
            )

            # Connect to system-client system-announce-port
            self.__seq.connect_ports(
                (
                    _ALSAPortMonitor.SEQ_CLIENT_SYSTEM,
                    _ALSAPortMonitor.SEQ_PORT_SYSTEM_ANNOUNCE,
                ),
                (self.__seq.client_id, self.__port),
            )

            # Start the event-loop
            self.__thread.start()
        except alsaseq.SequencerError:
            logger.exception(
                translate(
                    "MIDIError",
                    "Cannot create ALSA-MIDI port monitor, "
                    "MIDI connections/disconnections will not be detected.",
                )
            )

    def __loop(self):
        while True:
            for event in self.__seq.receive_events(timeout=-1, maxevents=1):
                if event.type == alsaseq.SEQ_EVENT_PORT_EXIT:
                    logger.debug("ALSA MIDI port deleted from system.")
                    self.port_removed.emit()
                elif event.type == alsaseq.SEQ_EVENT_PORT_START:
                    """
                    Some client may set it's name after the port creation.
                    Adding a small wait should ensure that the name are set when
                    we emit the signal.
                    """
                    sleep(0.05)
                    logger.debug("ALSA MIDI new port created.")
                    self.port_added.emit()


ALSAPortMonitor = _ALSAPortMonitor if alsaseq else PortMonitor
