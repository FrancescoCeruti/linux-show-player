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
from itertools import chain

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from lisp.core.decorators import memoize


@memoize
def load_icon(icon_name):
    """Return a QIcon from the icon theme.

    The loaded icons are cached.

    .. warning:
        QIcons should be loaded only from the QT main loop.
    """
    return QIcon.fromTheme(icon_name)


@memoize
def pixmap_from_icon(icon_name, size):
    """Return a QPixmap of "size x size" pixels from the icon theme.

    The returned pixmaps are cached.

    .. warning:
        QPixmap should be created only from the QT main loop.
    """
    return load_icon(icon_name).pixmap(size, size)


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


def translate(context, text, disambiguation=None, n=-1):
    return QApplication.translate(context, text, disambiguation, n)


def translate_many(context, texts):
    """Return a translate iterator."""
    for item in texts:
        yield translate(context, item)


def tr_sorted(context, iterable, key=None, reverse=False):
    """Return a new sorted list from the items in iterable.

    The sorting is done using translated versions of the iterable values.
    """
    if key is not None:
        def tr_key(item):
            translate(context, key(item))
    else:
        def tr_key(item):
            translate(context, item)

    return sorted(iterable, key=tr_key, reverse=reverse)\
