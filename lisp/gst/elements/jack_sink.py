##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

import jack

from lisp.gst.gst_element import GstMediaElement
from lisp.repository import Gst
from lisp.utils.decorators import synchronized


class JackSink(GstMediaElement):

    Type = GstMediaElement.TYPE_OUTPUT
    Name = 'JackSink'

    CLIENT_NAME = 'linux-show-player'
    CONNECT_MODE = 'none'

    _ControlClient = None
    _clients = []

    def __init__(self, pipe):
        super().__init__()

        if JackSink._ControlClient is None:
            JackSink._ControlClient = jack.Client('LinuxShowPlayer_Control')

        conns = self.get_default_connections(JackSink._ControlClient)
        self._properies = {'server': None,
                           'connections': conns,
                           'volume': 1,
                           'mute': False}

        self._volume = Gst.ElementFactory.make('volume', None)
        self._resample = Gst.ElementFactory.make('audioresample')
        self._sink = Gst.ElementFactory.make('jackaudiosink', 'sink')

        pipe.add(self._volume)
        pipe.add(self._resample)
        pipe.add(self._sink)

        self._client_id = self.__generate_client_id()
        self._client_name = JackSink.CLIENT_NAME + '-' + str(self._client_id)
        self._sink.set_property('client-name', self._client_name)
        self._sink.set_property('connect', JackSink.CONNECT_MODE)

        self._volume.link(self._resample)
        self._resample.link(self._sink)

        self._state = None
        self._bus = pipe.get_bus()
        self._bus.add_signal_watch()
        self._handler = self._bus.connect('message', self.__on_message)

    def dispose(self):
        self._bus.disconnect(self._handler)
        self._clients.remove(self._client_id)

        if len(self._clients) == 0:
            JackSink._ControlClient.close()
            JackSink._ControlClient = None

    def sink(self):
        return self._volume

    def properties(self):
        return self._properies

    def set_property(self, name, value):
        if name in self._properies:
            self._properies[name] = value
            if name == 'connections':
                if(self._state == Gst.State.PLAYING or
                   self._state == Gst.State.PAUSED):
                    self.__jack_connect()
            elif name in ['volume', 'mute']:
                self._volume.set_property(name, value)
            else:
                self._sink.set_property(name, value)

    @classmethod
    def get_default_connections(cls, client):
        # Up to 8 channels
        connections = [[] for _ in range(8)]

        # Search for default input ports
        input_ports = client.get_ports(name_pattern='^system:', is_audio=True,
                                       is_input=True)
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

    def __jack_connect(self):
        out_ports = JackSink._ControlClient.get_ports(
            name_pattern='^' + self._client_name + ':.+', is_audio=True)

        for port in out_ports:
            for conn_port in JackSink._ControlClient.get_all_connections(port):
                JackSink._ControlClient.disconnect(port, conn_port)

        for output, in_ports in enumerate(self._properies['connections']):
            for input_name in in_ports:
                if output < len(out_ports):
                    JackSink._ControlClient.connect(out_ports[output],
                                                    input_name)
                else:
                    break

    def __on_message(self, bus, message):
        if message.src == self._sink:
            if message.type == Gst.MessageType.STATE_CHANGED:
                change = message.parse_state_changed()
                self._state = change[1]

                # The jack ports are available when the the jackaudiosink
                # change from READY to PAUSED state
                if(change[0] == Gst.State.READY and
                   change[1] == Gst.State.PAUSED):
                    self.__jack_connect()
