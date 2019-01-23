# Python porting of qtractor fade functions
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
# along with Linux Show Player.  If not, see <http://www.gnu.org/licenses/>

"""
Functor arguments normalization:

t = (x - x0) / (x1 - x0)   where 'x' is the time  (x0 initial, x1 final)
a = y1 - y0                where 'y' is the value (y0 initial, y1 final)
b = y0
"""

from enum import Enum

from lisp.core.util import FunctionProxy


def fade_linear(t, a, b):
    """Linear fade."""
    return a * t + b


def fadein_quad(t, a, b):
    """Quadratic (t^2) fade in: accelerating from zero velocity."""
    return a * (t ** 2) + b


def fadeout_quad(t, a, b):
    """Quadratic (t^2) fade out: decelerating to zero velocity."""
    return a * (t * (2 - t)) + b


def fade_inout_quad(t, a, b):
    """Quadratic (t^2) fade in-out: acceleration until halfway,
    then deceleration.
    """
    t *= 2
    if t < 1.0:
        return 0.5 * a * (t ** 2) + b
    else:
        t -= 1
        return 0.5 * a * (1 - (t * (t - 2))) + b


def ntime(time, begin, duration):
    """Return normalized time."""
    return (time - begin) / (duration - begin)


class FadeInType(Enum):
    Linear = FunctionProxy(fade_linear)
    Quadratic = FunctionProxy(fadein_quad)
    Quadratic2 = FunctionProxy(fade_inout_quad)


class FadeOutType(Enum):
    Linear = FunctionProxy(fade_linear)
    Quadratic = FunctionProxy(fadeout_quad)
    Quadratic2 = FunctionProxy(fade_inout_quad)
