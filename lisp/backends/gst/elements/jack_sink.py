# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2015 Francesco Ceruti <ceppofrancy@gmail.com>
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

import jack

from lisp.backends.base.media_element import ElementType, MediaType
from lisp.backends.gst.gst_element import GstMediaElement
from lisp.backends.gst.gi_repository import Gst
from lisp.core.decorators import synchronized


class JackSink(GstMediaElement):
    ElementType = ElementType.Output
    MediaType = MediaType.Audio
    Name = 'JackSink'

    CLIENT_NAME = 'linux-show-player'
    CONNECT_MODE = 'none'

    _properties_ = ('server', 'connections')

    _ControlClient = None
    _clients = []

    def __init__(self, pipe):
        super().__init__()

        if JackSink._ControlClient is None:
            JackSink._ControlClient = jack.Client('LinuxShowPlayer_Control')

        self._resample = Gst.ElementFactory.make('audioresample')
        self._sink = Gst.ElementFactory.make('jackaudiosink', 'sink')

        self._client_id = self.__generate_client_id()
        self._client_name = JackSink.CLIENT_NAME + '-' + str(self._client_id)
        self._sink.set_property('client-name', self._client_name)
        self._sink.set_property('connect', JackSink.CONNECT_MODE)

        pipe.add(self._resample)
        pipe.add(self._sink)

        self._resample.link(self._sink)

        self.server = None
        self.connections = self.get_default_connections(JackSink._ControlClient)

        self._state = None
        self._bus = pipe.get_bus()
        self._bus.add_signal_watch()
        self._handler = self._bus.connect('message', self.__on_message)

        self.property_changed.connect(self.__property_changed)

    def sink(self):
        return self._resample

    def dispose(self):
        self._bus.disconnect(self._handler)
        self._clients.remove(self._client_id)

        if len(self._clients) == 0:
            JackSink._ControlClient.close()
            JackSink._ControlClient = None

    @classmethod
    def get_default_connections(cls, client):
        # Up to 8 channels
        connections = [[] for _ in range(8)]

        # Search for default input ports
        input_ports = client.get_ports(name_pattern='^system:', is_audio=True, is_input=True)
        for n, port in enumerate(input_ports):
            if n < len(connections):
                connections[n].append(port.name)
            else:
                break

        return connections

    @classmethod
    @synchronized
    def __generate_client_id(cls):
        n = 0
        for n, client in enumerate(cls._clients):
            if n != client:
                break

        if n == len(cls._clients) - 1:
            n += 1

        cls._clients.insert(n, n)
        return n

    def __property_changed(self, name, value):
        if name == 'connections':
            if self._state == Gst.State.PLAYING or self._state == Gst.State.PAUSED:
                self.__jack_connect()
        else:
            self._sink.set_property(name, value)

    def __jack_connect(self):
        out_ports = JackSink._ControlClient.get_ports(name_pattern='^' + self._client_name + ':.+', is_audio=True)

        for port in out_ports:
            for conn_port in JackSink._ControlClient.get_all_connections(port):
                JackSink._ControlClient.disconnect(port, conn_port)

        for output, in_ports in enumerate(self.connections):
            for input_name in in_ports:
                if output < len(out_ports):
                    JackSink._ControlClient.connect(out_ports[output], input_name)
                else:
                    break

    def __on_message(self, bus, message):
        if message.src == self._sink:
            if message.type == Gst.MessageType.STATE_CHANGED:
                change = message.parse_state_changed()
                self._state = change[1]

                # The jack ports are available when the the jackaudiosink change from READY to PAUSED state
                if change[0] == Gst.State.READY and change[1] == Gst.State.PAUSED:
                    self.__jack_connect()
