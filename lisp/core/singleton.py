# This file is part of Linux Show Player
#
# Copyright 2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

from abc import ABCMeta

from PyQt5.QtCore import QObject

from lisp.core.qmeta import QABCMeta


class Singleton(type):
    def __call__(cls, *args, **kwargs):
        try:
            return cls.__instance
        except AttributeError:
            pass

        cls.__instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.__instance

    @property
    def instance(cls):
        return cls.__instance


class ABCSingleton(ABCMeta):
    def __call__(cls, *args, **kwargs):
        try:
            return cls.__instance
        except AttributeError:
            pass

        cls.__instance = super(ABCSingleton, cls).__call__(*args, **kwargs)
        return cls.__instance

    @property
    def instance(cls):
        return cls.__instance


class QSingleton(type(QObject)):
    def __call__(cls, *args, **kwargs):
        try:
            return cls.__instance
        except AttributeError:
            pass

        cls.__instance = super(QSingleton, cls).__call__(*args, **kwargs)
        return cls.__instance

    @property
    def instance(cls):
        return cls.__instance


class QABCSingleton(QABCMeta):
    def __call__(cls, *args, **kwargs):
        try:
            return cls.__instance
        except AttributeError:
            pass

        cls.__instance = super(QABCSingleton, cls).__call__(*args, **kwargs)
        return cls.__instance

    @property
    def instance(cls):
        return cls.__instance
