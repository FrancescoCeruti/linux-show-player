# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2017 Francesco Ceruti <ceppofrancy@gmail.com>
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
from collections import deque
from enum import Enum
from liblo import ServerThread, Address, ServerError

from lisp.application import Application
from lisp.core.configuration import config
from lisp.core.signal import Signal
from lisp.core.singleton import ABCSingleton
from lisp.layouts.list_layout.layout import ListLayout


class OscMessageType(Enum):
    Int = 'Integer'
    Float = 'Float'
    Bool = 'Bool'
    String = 'String'


def callback_go(_, args, types):
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
        Application().layout.restart_all()


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
]


class OscCommon(metaclass=ABCSingleton):
    def __init__(self):
        self.__srv = None
        self.__listening = False
        self.__log = deque([], 10)

        self.new_message = Signal()

    def start(self):
        if self.__listening:
            return

        try:
            self.__srv = ServerThread(int(config['OSC']['inport']))

            if isinstance(Application().layout, ListLayout):
                for cb in GLOBAL_CALLBACKS:
                    self.__srv.add_method(cb[0], cb[1], cb[2])

            self.__srv.add_method(None, None, self.__new_message)

            self.__srv.start()
            self.__listening = True
            logging.info('OSC: Server started at {}'.format(self.__srv.url))
        except ServerError:
            logging.error('OSC: Cannot start sever')
            logging.debug(traceback.format_exc())

    def stop(self):
        if self.__srv is not None:
            if self.__listening:
                self.__srv.stop()
                self.__listening = False
            self.__srv.free()
            logging.info('OSC: Server stopped')

    @property
    def enabled(self):
        return config['OSC']['enabled'] == 'True'

    @property
    def listening(self):
        return self.__listening

    def send(self, path, *args):
        if self.__listening:
            target = Address(config['OSC']['hostname'],
                             int(config['OSC']['outport']))
            self.__srv.send(target, path, *args)

    def __new_message(self, path, args, types):
        # self.push_log(path, args, types, src, False)
        self.new_message.emit(path, args, types)
