# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

from lisp.core.singleton import ABCSingleton
from liblo import ServerThread, Address, ServerError

from lisp.core.configuration import config
from lisp.layouts.list_layout.layout import ListLayout
from lisp.ui import elogging
from lisp.ui.mainwindow import MainWindow
from lisp.application import Application
from lisp.cues.cue import CueState
from lisp.core.signal import Signal


# decorator for OSC callback (pushing messages to log, emits message_event)
def osc_handler(func):
   def func_wrapper(path, args, types, src):
       func(path, args, types, src)
       OscCommon().push_log(path, args, types, src)
       OscCommon().new_message.emit(path, args, types, src)
   return func_wrapper


@osc_handler
def _go(path, args, types, src):
    if isinstance(MainWindow().layout, ListLayout):
        MainWindow().layout.go()


@osc_handler
def _reset_list(path, args, types, src):
    if isinstance(MainWindow().layout, ListLayout):
        for cue in Application().cue_model:
            cue.stop()
        MainWindow().layout.set_current_index(0)


@osc_handler
def _pause_all(path, args, types, src):
    for cue in Application().cue_model:
        if cue.state == CueState.Running:
            cue.pause()


@osc_handler
def _restart_all(path, args, types, src):
    for cue in Application().cue_model:
        if cue.state == CueState.Pause:
            cue.start()


@osc_handler
def _stop_all(path, args, types, src):
    for cue in Application().cue_model:
        cue.stop()


class OscCommon(metaclass=ABCSingleton):
    def __init__(self):
        self.__srv = None
        self.__listening = False
        self.__log = deque([], 10)
        self.new_message = Signal()

        # TODO: static paths and callbacks, find smarter way
        self.__callbacks = [
            ['/lisp/go', '', _go],
            ['/lisp/reset', '', _reset_list],
            ['/lisp/pause', '', _pause_all],
            ['/lisp/start', '', _restart_all],
            ['/lisp/stop', '', _stop_all],
            [None, None, self.__new_message]
        ]

    def push_log(self, path, args, types, src, success=True):
        self.__log.append([path, args, types, src, success])

    def get_log(self):
        return self.__log

    def start(self):
        if self.__listening:
            return

        try:
            self.__srv = ServerThread(int(config['OSC']['inport']))
            for cb in self.__callbacks:
                self.__srv.add_method(cb[0], cb[1], cb[2])
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
    def listening(self):
        return self.__listening

    def send(self, path, *args):
        if self.__listening:
            target = Address(config['OSC']['hostname'], int(config['OSC']['outport']))
            self.__srv.send(target, path, *args)

    def __new_message(self, path, args, types, src):
        self.push_log(path, args, types, src, False)
        self.new_message.emit(path, args, types, src)
        # elogging.warning('OscCommon: unknown message received: {0} {1} {2}'.format(path, types, args), dialog=False)

    # def register_callback(self, path, typespec, func):
    #     # insert into callback list before callback, otherwise its ignored
    #     self.__callbacks.insert(-1, [path, typespec, func])
    #
    #     # fallback needs to be the registered callback
    #     self.__srv.del_method(None, None)
    #     self.__srv.add_method(path, typespec, func)
    #     self.__srv.add_method(None, None, self.__new_message)

    def activate_feedback(self, feedback):
        pass
