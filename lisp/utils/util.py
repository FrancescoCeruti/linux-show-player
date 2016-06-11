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

from collections import Mapping
from itertools import chain
from os import listdir, path
from os.path import isdir, exists, join

from PyQt5.QtWidgets import QApplication


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


def qfile_filters(extensions, allexts=True, anyfile=True):
    """Create a filter-string for a FileChooser.

    The result will be something like this: '<group1> (*.ext1 *.ext2);;
    <group2> (*.ext1)'

    :param extensions: The extensions as a dictionary {group: [extensions]}
    :type extensions: dict
    :param allexts: Add a group composed by all the given groups
    :type allexts: bool
    :param anyfile: Add the "Any File" group
    :type anyfile: bool
    :return: A QFileDialog filter-string
    :rtype: str
    """
    filters = []

    for key in extensions:
        filters.append(key.title() + ' (' + ' *.'.join(extensions[key]) + ')')

    filters.sort()

    if allexts:
        filters.insert(0, 'All supported (' +
                       ' *.'.join(chain(*extensions.values())) + ')')
    if anyfile:
        filters.append('Any file (*)')

    return ';;'.join(filters)


def file_path(base, filename):
    """Shortcut for path.abspath(path.join(path.dirname(base), filename))

    :param base: A file or a directory, used as reference path
    :type base: str

    :param filename: The file name to join with base
    :type filename: str
    """
    return path.abspath(path.join(path.dirname(base), filename))


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
    time = time_tuple(time)
    if time[0] > 0:
        return '%02d:%02d:%02d' % time[:-1]
    elif accurate:
        time = time[1:3] + (time[3] // 100,)
        return '%02d:%02d.%01d' % time + '0'
    else:
        return '%02d:%02d' % time[1:3] + '.00'


def compose_http_url(url, port, directory='/'):
    """Compose an http URL."""
    return 'http://' + url + ':' + str(port) + directory


def greatest_common_superclass(instances):
    classes = [type(x).mro() for x in instances]
    for x in classes[0]:
        if all(x in mro for mro in classes):
            return x


def subclasses(cls):
    for subclass in cls.__subclasses__():
        yield from subclasses(subclass)
        yield subclass


def weak_call_proxy(weakref):
    def proxy(*args, **kwargs):
        if weakref() is not None:
            weakref()(*args, **kwargs)

    return proxy


def translate(context, text, disambiguation=None, n=-1):
    return QApplication.translate(context, text, disambiguation, n)