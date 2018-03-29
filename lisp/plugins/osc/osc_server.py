# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2018 Francesco Ceruti <ceppofrancy@gmail.com>
# Copyright 2012-2016 Thomas Achtner <info@offtools.de>
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
import traceback
from enum import Enum
from liblo import ServerThread, ServerError
from threading import Lock

from lisp.core.signal import Signal

'''def callback_go(_, args, types):
    if not isinstance(Application().layout, ListLayout):
        return

    if (types == 'i' and args[0] == 1) or types == '':
        Application().layout.go()


def callback_reset(_, args, types):
    if not isinstance(Application().layout, ListLayout):
        return

    if (types == 'i' and args[0] == 1) or types == '':
        Application().layout.interrupt_all()
        Application().layout.set_current_index(0)


def callback_restart(_, args, types):
    if not isinstance(Application().layout, ListLayout):
        return

    if (types == 'i' and args[0] == 1) or types == '':
        Application().layout.resume_all()


def callback_pause(_, args, types):
    if not isinstance(Application().layout, ListLayout):
        return

    if (types == 'i' and args[0] == 1) or types == '':
        Application().layout.pause_all()


def callback_stop(_, args, types):
    if not isinstance(Application().layout, ListLayout):
        return

    if (types == 'i' and args[0] == 1) or types == '':
        Application().layout.stop_all()


def callback_select(_, args, types):
    if not isinstance(Application().layout, ListLayout):
        return

    if types == 'i' and args[0] > -1:
        Application().layout.set_current_index(args[0])


def callback_interrupt(_, args, types):
    if not isinstance(Application().layout, ListLayout):
        return

    if (types == 'i' and args[0] == 1) or types == '':
        Application().layout.interrupt_all()


GLOBAL_CALLBACKS = [
    ['/lisp/list/go', None, callback_go],
    ['/lisp/list/reset', None, callback_reset],
    ['/lisp/list/select', 'i', callback_select],
    ['/lisp/list/pause', None, callback_pause],
    ['/lisp/list/restart', None, callback_restart],
    ['/lisp/list/stop', None, callback_stop],
    ['/lisp/list/interrupt', None, callback_interrupt]
]'''

logger = logging.getLogger(__name__)


class OscMessageType(Enum):
    Int = 'Integer'
    Float = 'Float'
    Bool = 'Bool'
    String = 'String'


class OscServer:
    def __init__(self, hostname, in_port, out_port):
        self.__in_port = in_port
        self.__hostname = hostname
        self.__out_port = out_port

        self.__srv = None
        self.__running = False
        self.__lock = Lock()

        self.new_message = Signal()

    @property
    def out_port(self):
        return self.__out_port

    @out_port.setter
    def out_port(self, port):
        with self.__lock:
            self.__out_port = port

    @property
    def hostname(self):
        return self.__hostname

    @hostname.setter
    def hostname(self, hostname):
        with self.__lock:
            self.__hostname = hostname

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

    def start(self):
        if self.__running:
            return

        try:
            self.__srv = ServerThread(self.__in_port)
            self.__srv.add_method(None, None, self.new_message.emit)
            self.__srv.start()

            self.__running = True

            logger.info('OSC server started at {}'.format(self.__srv.url))
        except ServerError:
            logger.error('Cannot start OSC sever')
            logger.debug(traceback.format_exc())

    def stop(self):
        if self.__srv is not None:
            with self.__lock:
                if self.__running:
                    self.__srv.stop()
                    self.__running = False

            self.__srv.free()
            logger.info('OSC server stopped')

    def send(self, path, *args):
        with self.__lock:
            if self.__running:
                self.__srv.send((self.__hostname, self.__out_port), path, *args)
