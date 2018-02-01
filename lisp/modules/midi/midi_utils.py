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

from lisp.core.configuration import config

#: Define MIDI message attributes as {name : (min, max, default)}
MIDI_ATTRIBUTES = {
    'channel': (0, 15, 0),
    'note': (0, 127, 0),
    'velocity': (0, 127, 64),
    'control': (0, 127, 0),
    'program': (0, 127, 0),
    'value': (0, 127, 0),
    'song': (0, 127, 0),
    'pitch': (-8192, 8191, 0),
    'pos': (0, 16383, 0)
}


#: Define MIDI message types as {name : (attribute1, ..., attributeN)}
MIDI_MESSAGES = {
    'note_on': ('channel', 'note', 'velocity'),
    'note_off': ('channel', 'note', 'velocity'),
    'control_change': ('channel', 'control', 'value'),
    'program_change': ('channel', 'program',),
    'polytouch': ('channel', 'note', 'value'),
    'pitchwheel': ('channel', 'pitch',),
    'song_select': ('song',),
    'songpos': ('pos',),
    'start': (),
    'stop': (),
    'continue': (),
}


def str_msg_to_dict(str_message):
    message = mido.parse_string(str_message)
    dict_message = {'type': message.type}

    for name in MIDI_MESSAGES.get(message.type, ()):
        dict_message[name] = getattr(message, name)

    return dict_message


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


def mido_port_name(port_name, mode):
    """Transform application default-port to appropriate values for mido

    :param port_name: port-name to be checked
    :param mode: port I/O mode ['I'=input, 'O'=output]
    :return: the port-name to give to mido to open the right port
    """
    port_name = port_name

    if port_name == 'AppDefault':
        if mode.upper() == 'I':
            port_name = config['MIDI']['InputDevice']
        elif mode.upper() == 'O':
            port_name = config['MIDI']['OutputDevice']

    if port_name == 'SysDefault':
        return None
    elif mode.upper() == 'I' and port_name in mido_backend().get_input_names():
        return port_name
    elif mode.upper() == 'O' and port_name in mido_backend().get_output_names():
        return port_name
