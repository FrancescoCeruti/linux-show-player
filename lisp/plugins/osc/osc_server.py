# This file is part of Linux Show Player
#
# Copyright 2024 Francesco Ceruti <ceppofrancy@gmail.com>
# Copyright 2016 Thomas Achtner <info@offtools.de>
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
from threading import Lock, Thread

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

from lisp.core.signal import Signal
from lisp.core.util import EqEnum, get_lan_ip
from lisp.ui.ui_utils import translate

logger = logging.getLogger(__name__)


class OscMessageType(EqEnum):
    Int = "Integer"
    Float = "Float"
    Bool = "Bool"
    String = "String"


class OscServer:
    def __init__(self, hostname, in_port, out_port):
        self.__in_port = in_port
        self.__hostname = hostname
        self.__out_port = out_port

        # Receives messages
        self.__srv = None
        self.__thread = None
        self.__running = False

        # Sends messages
        self.__client = None
        self.__lock = Lock()

        self.new_message = Signal()
        self.new_message.connect(self.__log_message)

        self.__dispatcher = Dispatcher()
        self.__dispatcher.set_default_handler(
            self.new_message.emit, needs_reply_address=True
        )

    @property
    def out_port(self):
        return self.__out_port

    @out_port.setter
    def out_port(self, port):
        self.__out_port = port
        self.__renew_client()

    @property
    def hostname(self):
        return self.__hostname

    @hostname.setter
    def hostname(self, hostname):
        self.__hostname = hostname
        self.__renew_client()

    @property
    def in_port(self):
        return self.__in_port

    @in_port.setter
    def in_port(self, port):
        self.__in_port = port
        self.stop()
        self.start()

    def is_running(self):
        return self.__running

    def __renew_client(self):
        with self.__lock:
            self.__client = SimpleUDPClient(self.__hostname, self.__out_port)

    def start(self):
        if self.__running:
            return

        try:
            self.__srv = ThreadingOSCUDPServer(
                (get_lan_ip(), self.__in_port), self.__dispatcher
            )

            self.__thread = Thread(target=self.__srv.serve_forever)
            self.__thread.start()

            self.__running = True

            logger.info(
                translate("OscServerInfo", "OSC server started at {}").format(
                    self.__srv.server_address
                )
            )
        except Exception:
            logger.exception(
                translate("OscServerError", "Cannot start OSC server")
            )

    def stop(self):
        if self.__srv is not None:
            if self.__running:
                self.__srv.shutdown()
                self.__srv.server_close()
                self.__running = False

            logger.info(translate("OscServerInfo", "OSC server stopped"))

    def send(self, path, *args):
        if self.__client is None:
            self.__renew_client()

        with self.__lock:
            self.__client.send_message(path, args)

    def __log_message(self, src, path, *args):
        logger.debug(
            translate(
                "OscServerDebug", 'Message from {}:{} -> path: "{}" args: {}'
            ).format(*src, path, args)
        )
