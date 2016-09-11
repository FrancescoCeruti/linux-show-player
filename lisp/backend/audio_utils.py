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

import aifc
import math
import sunau
import urllib.parse
import wave

# Decibel value to be considered -inf
MIN_VOLUME_DB = -144
# Linear value of MIN_VOLUME_DB
MIN_VOLUME = 6.30957344480193e-08
# Maximum linear value for the volume, equals to 1000%
MAX_VOLUME = 10
# Decibel value of MAX_VOLUME
MAX_VOLUME_DB = 20


def db_to_linear(value, min_db_zero=True):
    """dB value to linear value conversion."""
    if min_db_zero and value <= MIN_VOLUME_DB:
        return 0

    return 10 ** (value / 20)


def linear_to_db(value):
    """Linear value to dB value conversion."""
    return 20 * math.log10(value) if value > MIN_VOLUME else MIN_VOLUME_DB


def fader_to_slider(value):
    """Inverse function of `slider_to_fader`.

    Note::
        If converting back to an integer scale use `round()` instead of `int()`
    """
    return (value / 3.16227766) ** (1 / 3.7)


def slider_to_fader(value):
    """Convert a slider linear value to a fader-like scale.

    The formula used is the following:
        (10db) * (x ^ 3.7)

    Where 10db = 3.16227766
    And 0.0 <= x <= 1.0

    :param value: The value to scale [0-1]
    :type value: float
    """
    if value > 1.0:
        value = 1.0
    elif value < 0.0:
        value = 0

    return 3.16227766 * (value ** 3.7)


def python_duration(path, sound_module):
    """Returns audio-file duration using the given standard library module."""
    duration = 0
    try:
        with sound_module.open(path, 'r') as file:
            frames = file.getnframes()
            rate = file.getframerate()
            duration = int(frames / rate * 1000)
    finally:
        return duration


def uri_duration(uri):
    """Return the audio-file duration, using the given uri"""
    protocol, path = uri.split('://')
    path = urllib.parse.unquote(path)

    if protocol == 'file':
        for mod in [wave, aifc, sunau]:
            duration = python_duration(path, mod)
            if duration > 0:
                return duration

    return 0
