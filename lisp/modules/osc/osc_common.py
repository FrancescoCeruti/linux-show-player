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
from lisp.utils import elogging


class OscCommon(metaclass=ABCSingleton):
    def __init__(self):
        self.__srv = None
        self.__listening = False
        self.__callbacks = []

    def start(self):
        self.stop()
        try:
            self.__srv = ServerThread(config['OSC']['port'])
            for cb in self.__callbacks:
                self.__srv.add_method(cb[0], cb[1], cb[2])
            self.__srv.start()
            self.__listening = True
        except ServerError as e:
            elogging.error(e, dialog=False)

    def stop(self):
        if self.__listening:
            self.__srv.stop()
            self.__listening = False
        self.__srv.free()

    def send(self, path, *args):
        if self.__listening:
            target = Address(config['OSC']['hostname'], config['OSC']['port'])
            self.__srv.send(target, path, *args)

    def register_callback(self, path, typespec, func):
        self.__callbacks.append([path, typespec, func])
