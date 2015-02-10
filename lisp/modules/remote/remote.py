##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from http.client import HTTPConnection
import logging
import socket
from threading import Thread
from xmlrpc.client import ServerProxy, Fault, Transport
from xmlrpc.server import SimpleXMLRPCServer

from lisp.utils.configuration import config

from lisp.application import Application
from lisp.core.singleton import Singleton
from lisp.cues.cue import Cue
from lisp.cues.media_cue import MediaCue
from lisp.modules.remote.discovery import Announcer


def initialize():
    # Using 'localhost' or similar make the server unreachable from outside
    ip = socket.gethostbyname(socket.gethostname())
    port = int(config['Remote']['BindPort'])

    RemoteController(ip=ip, port=port)
    RemoteController().start()


def terminate():
    RemoteController().stop()


def compose_uri(url, port, directory='/'):
    return 'http://' + url + ':' + str(port) + directory


class RemoteDispatcher:

    # Layout functions

    def get_cue_at(self, index):
        cue = Application().layout.get_cue_at(index)
        if cue is not None:
            return cue.properties()
        return {}

    def get_cues(self, cue_class=Cue):
        cues = Application().layout.get_cues(cue_class)
        return [cue.properties() for cue in cues]

    # Cue function

    def execute(self, index):
        cue = Application().layout.get_cue_at(index)
        if cue is not None:
            cue.execute(emit=False)

    # MediaCue functions

    def play(self, index):
        cue = Application().layout.get_cue_at(index)
        if isinstance(cue, MediaCue):
            cue.media.play()

    def pause(self, index):
        cue = Application().layout.get_cue_at(index)
        if isinstance(cue, MediaCue):
            cue.media.pause()

    def stop(self, index):
        cue = Application().layout.get_cue_at(index)
        if isinstance(cue, MediaCue):
            cue.media.stop()

    def seek(self, index, position):
        cue = Application().layout.get_cue_at(index)
        if isinstance(cue, MediaCue):
            cue.media.seek(position)


class TimeoutTransport(Transport):

    timeout = 2.0

    def set_timeout(self, timeout):
        self.timeout = timeout

    def make_connection(self, host):
        return HTTPConnection(host, timeout=self.timeout)


class RemoteController(Thread, metaclass=Singleton):

    def __init__(self, ip='localhost', port=8070):
        super().__init__(daemon=True)
        self.setName('RemoteController')

        self.server = SimpleXMLRPCServer((ip, port), allow_none=True,
                                         logRequests=False)

        self.server.register_introspection_functions()
        self.server.register_instance(RemoteDispatcher())

        self._announcer = Announcer()

    def start(self):
        self._announcer.start()
        Thread.start(self)

    def run(self):
        logging.info('REMOTE: Session started at ' +
                     str(self.server.server_address))

        self.server.serve_forever()

        logging.info('REMOTE: Session ended')

    def stop(self):
        self.server.shutdown()
        self._announcer.stop()

    @staticmethod
    def connect_to(uri):
        proxy = ServerProxy(uri, transport=TimeoutTransport())

        try:
            # Call a fictive method.
            proxy._()
        except Fault:
            # Connected, the method doesn't exist, which is expected.
            pass
        except socket.error:
            # Not connected, socket error mean that the service is unreachable.
            raise Exception('Session at ' + uri + ' is unreachable')

        # Just in case the method is registered in the XmlRPC server
        return proxy
