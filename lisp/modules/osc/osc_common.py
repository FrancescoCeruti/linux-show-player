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
from lisp.ui.mainwindow import MainWindow
from lisp.application import Application
from lisp.cues.cue import CueState
from lisp.core.signal import Signal

# TODO: add osc log as queue and dialog to show it


class OscMessageType(Enum):
    Int = 'Integer'
    Float = 'Float'
    Bool = 'Bool'
    String = 'String'

# decorator for OSC callback (pushing messages to log, emits message_event)
# def __osc_handler(func):
#    def func_wrapper(path, args, types):
#        func()
#        # OscCommon().push_log(path, args, types, src)
#        OscCommon().new_message.emit(path, args, types)
#    return func_wrapper


# @__osc_handler
def _go():
    """triggers GO in ListLayout"""
    if isinstance(MainWindow().layout, ListLayout):
        MainWindow().layout.go()


# @__osc_handler
def _list_reset():
    """reset, stops all cues, sets cursor to Cue index 0 in ListLayout"""
    if isinstance(MainWindow().layout, ListLayout):
        for cue in Application().cue_model:
            cue.stop()
        MainWindow().layout.set_current_index(0)


# @__osc_handler
def _list_cursor(path, args, types):
    """sets cursor to given Cue index in ListLayout"""
    if not isinstance(MainWindow().layout, ListLayout):
        MainWindow().layout.set_current_index(0)
        return

    if path == '/lisp/list/cursor' and types == 'i':
        index = args[0]
        MainWindow().layout.set_current_index(index)


# @__osc_handler
def _pause_all():
    """triggers global pause all media"""
    for cue in Application().cue_model:
        if cue.state == CueState.Running:
            cue.pause(True)


# @__osc_handler
def _play_all():
    """triggers global play, if pausing"""
    for cue in Application().cue_model:
        if cue.state == CueState.Pause:
            cue.start(True)


# TODO: add fade as option to message?
# @__osc_handler
def _stop_all():
    """triggers global stop, stops all media cues"""
    for cue in Application().cue_model:
        cue.stop(True)


class OscCommon(metaclass=ABCSingleton):
    def __init__(self):
        self.__srv = None
        self.__listening = False
        self.__log = deque([], 10)
        self.new_message = Signal()

        # TODO: static paths and callbacks, make it editable through settings dialog
        self.__callbacks = [
            ['/lisp/list/go', None, _go],
            ['/lisp/list/reset', None, _list_reset],
            ['/lisp/list/cursor', 'i', _list_cursor],
            ['/lisp/pause', None, _pause_all],
            ['/lisp/play', None, _play_all],
            ['/lisp/stop', None, _stop_all],
            [None, None, self.__new_message]
        ]

    # def push_log(self, path, args, types, src, success=True):
    #     self.__log.append([path, args, types, src, success])
    #
    # def get_log(self):
    #     return self.__log

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

    def __new_message(self, path, args, types):
        # self.push_log(path, args, types, src, False)
        self.new_message.emit(path, args, types)
