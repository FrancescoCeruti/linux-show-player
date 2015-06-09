# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2015 Francesco Ceruti <ceppofrancy@gmail.com>
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

import math
import wave
import aifc
import sunau
import urllib.parse


#: Linear value for -100dB
MIN_dB = 0.000000312


def db_to_linear(value):
    """dB value to linear value conversion."""
    return math.pow(10, value / 20)


def linear_to_db(value):
    """Linear value to dB value conversion."""
    return 20 * math.log10(value) if value > MIN_dB else -100


def python_duration(path, sound_module):
    """Returns audio-file duration using the given standard library module."""
    duration = 0
    try:
        with sound_module.open(path, 'r') as file:
            frames = file.getnframes()
            rate = file.getframerate()
            duration = (frames // float(rate)) * 1000
    finally:
        return duration


def uri_duration(uri):
    """Return the audio-file duration, using the given uri"""
    protocol, path = uri.split('://')
    path = urllib.parse.unquote(path)

    if protocol == 'file':
        if path.lower().endswith(('.wav', '.wave')):
            return python_duration(path, wave)
        if path.lower().endswith(('.au', '.snd')):
            return python_duration(path, sunau)
        if path.lower().endswith(('.aiff', '.aif', '.aifc')):
            return python_duration(path, aifc)

    return 0
