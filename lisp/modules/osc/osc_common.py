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


from lisp.core.singleton import ABCSingleton
from liblo import ServerThread, Address, ServerError

from lisp.utils.configuration import config
from lisp.layouts.list_layout.layout import ListLayout
from lisp.utils import elogging
from lisp.ui.mainwindow import MainWindow
from lisp.application import Application
from lisp.cues.cue import Cue, CueState


def _go(path, args, types, src):
    go = int(args[0])
    if isinstance(MainWindow().layout, ListLayout):
        if go >= 1:
            MainWindow().layout.go()


def _pause_all(path, args, types, src):
    pause = int(args[0])
    for cue in Application().cue_model:
        if cue.state == CueState.Running and pause >= 1:
            cue.start()


def _restart_all(path, args, types, src):
    restart = int(args[0])
    for cue in Application().cue_model:
        if cue.state == CueState.Pause and restart >= 1:
            cue.start()


def _stop_all(path, args, types, src):
    stop = int(args[0])
    if stop >= 1:
        for cue in Application().cue_model:
            cue.stop()


class OscCommon(metaclass=ABCSingleton):
    def __init__(self):
        self.__srv = None
        self.__listening = False

        # TODO: static paths and callbacks, find smarter way
        self.__callbacks = [
            ['/lisp/go', 'i', _go],
            ['/lisp/pause', 'i', _pause_all],
            ['/lisp/start', 'i', _restart_all],
            ['/lisp/stop', 'i', _stop_all],
        ]

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

    def send(self, path, *args):
        if self.__listening:
            target = Address(config['OSC']['hostname'], int(config['OSC']['outport']))
            self.__srv.send(target, path, *args)

    def register_callback(self, path, typespec, func):
        self.__callbacks.append([path, typespec, func])

    def activate_feedback(self, feedback):
        pass