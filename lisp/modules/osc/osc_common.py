# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

from collections import deque
from enum import Enum

from lisp.core.singleton import ABCSingleton
from liblo import ServerThread, Address, ServerError

from lisp.core.configuration import config
from lisp.layouts.list_layout.layout import ListLayout
from lisp.ui import elogging
from lisp.application import Application
from lisp.core.signal import Signal


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


class OscCommon(metaclass=ABCSingleton):
    def __init__(self):
        self.__srv = None
        self.__listening = False
        self.__log = deque([], 10)
        self.new_message = Signal()

        self.__callbacks = [
            ['/lisp/list/go', None, callback_go],
            ['/lisp/list/reset', None, callback_reset],
            ['/lisp/list/select', 'i', callback_select],
            ['/lisp/list/pause', None, callback_pause],
            ['/lisp/list/restart', None, callback_restart],
            ['/lisp/list/stop', None, callback_stop],
            ['/lisp/list/interrupt', None, callback_interrupt]
        ]

    def start(self):
        if self.__listening:
            return

        try:
            self.__srv = ServerThread(int(config['OSC']['inport']))

            if isinstance(Application().layout, ListLayout):
                for cb in self.__callbacks:
                    self.__srv.add_method(cb[0], cb[1], cb[2])

            self.__srv.add_method(None, None, self.__new_message)

            self.__srv.start()
            self.__listening = True
            elogging.info('OSC: Server started ' + self.__srv.url, dialog=False)
        except ServerError as e:
            elogging.error(e, dialog=False)

    def stop(self):
        if self.__srv:
            if self.__listening:
                self.__srv.stop()
                self.__listening = False
            self.__srv.free()
            elogging.info('OSC: Server stopped', dialog=False)

    @property
    def enabled(self):
        return config['OSC']['enabled'] == 'True'

    @property
    def listening(self):
        return self.__listening

    def send(self, path, *args):
        if self.__listening:
            target = Address(config['OSC']['hostname'], int(config['OSC']['outport']))
            self.__srv.send(target, path, *args)

    def __new_message(self, path, args, types):
        # self.push_log(path, args, types, src, False)
        self.new_message.emit(path, args, types)
