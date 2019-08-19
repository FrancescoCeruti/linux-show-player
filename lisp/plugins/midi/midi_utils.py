# This file is part of Linux Show Player
#
# Copyright 2019 Francesco Ceruti <ceppofrancy@gmail.com>
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

from typing import Iterable

import mido
from PyQt5.QtCore import QT_TRANSLATE_NOOP
from mido import Message

MIDI_MSGS_SPEC = {
    "note_on": ["channel", "note", "velocity"],
    "note_off": ["channel", "note", "velocity"],
    "polytouch": ["channel", "note", "value"],
    "control_change": ["channel", "control", "value"],
    "program_change": ["channel", "program", None],
    "aftertouch": ["channel", "value", None],
    "pitchwheel": ["channel", "pitch", None],
    "song_select": ["song", None, None],
    "songpos": ["pos", None, None],
    "start": [None] * 3,
    "stop": [None] * 3,
    "continue": [None] * 3,
}

MIDI_ATTRS_SPEC = {
    "channel": (1, 16, -1),
    "note": (0, 127, 0),
    "velocity": (0, 127, 0),
    "control": (0, 127, 0),
    "program": (0, 127, 0),
    "value": (0, 127, 0),
    "song": (0, 127, 0),
    "pitch": (-8192, 8191, 0),
    "pos": (0, 16383, 0),
}

MIDI_MSGS_NAME = {
    "note_on": QT_TRANSLATE_NOOP("MIDIMessageType", "Note ON"),
    "note_off": QT_TRANSLATE_NOOP("MIDIMessageType", "Note OFF"),
    "polytouch": QT_TRANSLATE_NOOP("MIDIMessageType", "Polyphonic After-touch"),
    "control_change": QT_TRANSLATE_NOOP(
        "MIDIMessageType", "Control/Mode Change"
    ),
    "program_change": QT_TRANSLATE_NOOP("MIDIMessageType", "Program Change"),
    "aftertouch": QT_TRANSLATE_NOOP("MIDIMessageType", "Channel After-touch"),
    "pitchwheel": QT_TRANSLATE_NOOP("MIDIMessageType", "Pitch Bend Change"),
    "song_select": QT_TRANSLATE_NOOP("MIDIMessageType", "Song Select"),
    "songpos": QT_TRANSLATE_NOOP("MIDIMessageType", "Song Position"),
    "start": QT_TRANSLATE_NOOP("MIDIMessageType", "Start"),
    "stop": QT_TRANSLATE_NOOP("MIDIMessageType", "Stop"),
    "continue": QT_TRANSLATE_NOOP("MIDIMessageType", "Continue"),
}

MIDI_ATTRS_NAME = {
    "channel": QT_TRANSLATE_NOOP("MIDIMessageAttr", "Channel"),
    "note": QT_TRANSLATE_NOOP("MIDIMessageAttr", "Note"),
    "velocity": QT_TRANSLATE_NOOP("MIDIMessageAttr", "Velocity"),
    "control": QT_TRANSLATE_NOOP("MIDIMessageAttr", "Control"),
    "program": QT_TRANSLATE_NOOP("MIDIMessageAttr", "Program"),
    "value": QT_TRANSLATE_NOOP("MIDIMessageAttr", "Value"),
    "song": QT_TRANSLATE_NOOP("MIDIMessageAttr", "Song"),
    "pitch": QT_TRANSLATE_NOOP("MIDIMessageAttr", "Pitch"),
    "pos": QT_TRANSLATE_NOOP("MIDIMessageAttr", "Position"),
}


def midi_str_to_dict(midi_str: str) -> dict:
    return mido.parse_string(midi_str).dict()


def midi_dict_to_str(midi_dict: dict) -> str:
    message = mido.Message.from_dict(midi_dict)
    return mido.format_as_string(message, include_time=False)


def midi_data_from_msg(message) -> list:
    data = []

    for attr in MIDI_MSGS_SPEC.get(message.type, ()):
        if attr is not None:
            data.append(getattr(message, attr, None))

    return data


def midi_data_from_dict(midi_dict: dict) -> list:
    return midi_data_from_msg(midi_from_dict(midi_dict))


def midi_msg_from_data(message_type: str, data: Iterable):
    message_spec = MIDI_MSGS_SPEC.get(message_type, ())
    message = Message(message_type)

    for attr, value in zip(message_spec, data):
        if attr is not None:
            setattr(message, attr, value)

    return message


def midi_from_dict(midi_dict: dict):
    return mido.Message.from_dict(midi_dict)


def midi_from_str(midi_str: str):
    return mido.Message.from_str(midi_str)


def mido_backend():
    """Return the current backend object, or None"""
    backend = None

    if hasattr(mido, "backend"):
        backend = mido.backend

    if backend is None:
        raise RuntimeError("MIDI backend not loaded")

    return backend
