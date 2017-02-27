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

import re
import socket
from collections import Mapping
from enum import Enum
from os import listdir
from os.path import isdir, exists, join

import functools


def deep_update(d1, d2):
    """Recursively update d1 with d2"""
    for key in d2:
        if key not in d1:
            d1[key] = d2[key]
        elif isinstance(d2[key], Mapping) and isinstance(d1[key], Mapping):
            d1[key] = deep_update(d1[key], d2[key])
        else:
            d1[key] = d2[key]

    return d1


def find_packages(path='.'):
    """List the python packages in the given directory."""

    return [d for d in listdir(path) if isdir(join(path, d)) and
            exists(join(path, d, '__init__.py'))]


def time_tuple(millis):
    """Split the given time in a tuple.

    :param millis: Number of milliseconds
    :type millis: int

    :return (hours, minutes, seconds, milliseconds)
    """
    seconds, millis = divmod(millis, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    return hours, minutes, seconds, millis


def strtime(time, accurate=False):
    """Return a string from the given milliseconds time.

    :returns:
        hh:mm:ss when > 59min
        mm:ss:00 when < 1h and accurate=False
        mm:ss:z0 when < 1h and accurate=True
    """
    # Cast time to int to avoid formatting problems
    time = time_tuple(int(time))
    if time[0] > 0:
        return '{:02}:{:02}:{:02}'.format(*time[:-1])
    elif accurate:
        return '{:02}:{:02}.{}0'.format(time[1], time[2], time[3] // 100)
    else:
        return '{:02}:{:02}.00'.format(*time[1:3])


def compose_http_url(url, port, directory='/'):
    """Compose an http URL."""
    return 'http://' + url + ':' + str(port) + directory


def greatest_common_superclass(instances):
    classes = [type(x).mro() for x in instances]
    for x in classes[0]:
        if all(x in mro for mro in classes):
            return x


def get_lan_ip():
    """Return active interface LAN IP, or localhost if no address is assigned.

    From: http://stackoverflow.com/a/28950776/5773767
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't have to be reachable
        s.connect(('10.255.255.255', 0))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def subclasses(cls):
    for subclass in cls.__subclasses__():
        yield from subclasses(subclass)
        yield subclass


def weak_call_proxy(weakref):
    def proxy(*args, **kwargs):
        if weakref() is not None:
            weakref()(*args, **kwargs)

    return proxy


def natural_keys(text):
    """Turn a string into a list of string and number chunks.

    "z23a" -> ["z", 23, "a"]

    From: http://stackoverflow.com/a/5967539/5773767

    .. highlight::

        l = ['something1', 'something17', 'something4']
        l.sort(key=natural_keys) # sorts in human order
        ['something1', 'something4', 'something17']
    """
    return [int(c) if c.isdigit() else c for c in re.split('(\d+)', text)]


def rhasattr(obj, attr):
    """Check object's attribute, can use dot notation.

    .. highlight::

        class A: pass
        a = A()
        a.b = A()
        a.b.c = 42
        hasattr(a, 'b.c')  # True
    """
    return functools.reduce(hasattr, attr.split('.'), obj)


def rsetattr(obj, attr, value):
    """Set object's attribute, can use dot notation.

    From: http://stackoverflow.com/a/31174427/5773767

    .. highlight::

        class A: pass
        a = A()
        a.b = A()
        a.b.c = 0
        rsetattr(a, 'b.c', 42)
        a.b.c  # 42
    """
    pre, _, post = attr.rpartition('.')
    setattr(rgetattr(obj, pre) if pre else obj, post, value)


rgetattr_sentinel = object()


def rgetattr(obj, attr, default=rgetattr_sentinel):
    """Get object's attribute, can use dot notation.

    From: http://stackoverflow.com/a/31174427/5773767

    .. highlight::

        class A: pass
        a = A()
        a.b = A()
        a.b.c = 24
        rgetattr(a, 'b.c')  # 42
    """
    if default is rgetattr_sentinel:
        _getattr = getattr
    else:
        def _getattr(obj, name):
            return getattr(obj, name, default)

    return functools.reduce(_getattr, attr.split('.'), obj)


class EqEnum(Enum):
    """Value-comparable Enum.

    EqEnum members can be compared for equality with their values:

    .. highlight::

        class E(EqEnum):
            A = 10

        class E2(EqEnum):
            A2 = 10

        # Equality NOT identity
        E.A == 10  # True
        E.A is 10  # False

        E.A == E.A2  # False
    """

    def __eq__(self, other):
        if not isinstance(other, Enum):
            return self.value == other

        return super().__eq__(other)


class FunctionProxy:
    """Allow to mask a function as an Object.

    Can be useful in enum.Enum (Python enumeration) to have callable values.
    """
    def __init__(self, function):
        self.function = function

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)
