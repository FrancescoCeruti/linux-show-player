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

import mido

from lisp.core.configuration import AppConfig


def str_msg_to_dict(str_message):
    message = mido.parse_string(str_message)
    dict_msg = {'type': message.type}

    for name in message._spec.arguments:
        dict_msg[name] = getattr(message, name)

    return dict_msg


def dict_msg_to_str(dict_message):
    msg_type = dict_message.pop('type')
    message = mido.Message(msg_type, **dict_message)

    return mido.format_as_string(message, include_time=False)


def mido_backend():
    """Return the current backend object, or None"""
    backend = None

    if hasattr(mido, 'backend'):
        backend = mido.backend

    if backend is None:
        raise RuntimeError('MIDI backend not loaded')

    return backend

