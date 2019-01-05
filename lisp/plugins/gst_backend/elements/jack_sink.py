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

import logging

import jack
from PyQt5.QtCore import QT_TRANSLATE_NOOP

from lisp.backend.media_element import ElementType, MediaType
from lisp.core.properties import Property
from lisp.plugins.gst_backend.gi_repository import Gst
from lisp.plugins.gst_backend.gst_element import GstMediaElement
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)


class JackSink(GstMediaElement):
    ElementType = ElementType.Output
    MediaType = MediaType.Audio
    Name = QT_TRANSLATE_NOOP("MediaElementName", "JACK Out")

    CLIENT_NAME = "linux-show-player"
    CONNECT_MODE = "none"

    _ControlClient = None
    _clients = []

    connections = Property(default=[])

    def __init__(self, pipeline):
        super().__init__(pipeline)

        if JackSink._ControlClient is None:
            JackSink._ControlClient = jack.Client(
                "LinuxShowPlayer_Control", no_start_server=True
            )

        self.pipeline = pipeline
        self.audio_resample = Gst.ElementFactory.make("audioresample")
        self.jack_sink = Gst.ElementFactory.make("jackaudiosink", "sink")

        self._client_id = JackSink.__register_client_id()
        self._client_name = JackSink.CLIENT_NAME + "-" + str(self._client_id)
        self.jack_sink.set_property("client-name", self._client_name)
        self.jack_sink.set_property("connect", JackSink.CONNECT_MODE)

        self.pipeline.add(self.audio_resample)
        self.pipeline.add(self.jack_sink)

        self.audio_resample.link(self.jack_sink)

        self.connections = self.default_connections(JackSink._ControlClient)
        self.changed("connections").connect(self.__prepare_connections)

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        self._handler = bus.connect("message", self.__on_message)

    def sink(self):
        return self.audio_resample

    def dispose(self):
        try:
            self.pipeline.get_bus().disconnect(self._handler)
            JackSink._clients.remove(self._client_id)
        finally:
            if not JackSink._clients:
                JackSink._ControlClient.close()
                JackSink._ControlClient = None

    @classmethod
    def default_connections(cls, client):
        # Up to 8 channels
        connections = [[] for _ in range(8)]

        if isinstance(client, jack.Client):
            # Search for default input ports
            input_ports = client.get_ports(
                name_pattern="^system:", is_audio=True, is_input=True
            )
            for n, port in enumerate(input_ports):
                if n < len(connections):
                    connections[n].append(port.name)
                else:
                    break

        return connections

    def __prepare_connections(self, value):
        if (
            self.pipeline.current_state == Gst.State.PLAYING
            or self.pipeline.current_state == Gst.State.PAUSED
        ):
            self.__jack_connect()

    @classmethod
    def __register_client_id(cls):
        n = 0
        for n, client in enumerate(cls._clients):
            if n != client:
                break

        if n == len(cls._clients) - 1:
            n += 1

        cls._clients.insert(n, n)
        return n

    def __jack_connect(self):
        out_ports = JackSink._ControlClient.get_ports(
            name_pattern="^" + self._client_name + ":.+", is_audio=True
        )

        for port in out_ports:
            for conn_port in JackSink._ControlClient.get_all_connections(port):
                try:
                    JackSink._ControlClient.disconnect(port, conn_port)
                except jack.JackError:
                    logger.exception(
                        translate(
                            "JackSinkError",
                            "An error occurred while disconnection Jack ports",
                        )
                    )

        for output, in_ports in enumerate(self.connections):
            for input_name in in_ports:
                if output < len(out_ports):
                    try:
                        JackSink._ControlClient.connect(
                            out_ports[output], input_name
                        )
                    except jack.JackError:
                        logger.exception(
                            "An error occurred while connecting Jack ports"
                        )
                else:
                    break

    def __on_message(self, bus, message):
        if message.src == self.jack_sink:
            if message.type == Gst.MessageType.STATE_CHANGED:
                change = tuple(message.parse_state_changed())[0:2]

                # The jack ports are available when the the jackaudiosink
                # change from READY to PAUSED state
                if change == (Gst.State.READY, Gst.State.PAUSED):
                    self.__jack_connect()
