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

import fcntl
from itertools import chain

import logging
import os
import signal
from PyQt5.QtCore import QTranslator, QLocale, QSocketNotifier
from PyQt5.QtWidgets import QApplication, qApp

from lisp import I18N_PATH

logger = logging.getLogger(__name__)


def adjust_widget_position(widget):
    """Adjust the widget position to ensure it's in the desktop.

    :type widget: PyQt5.QtWidgets.QWidget.QWidget
    """
    widget.setGeometry(adjust_position(widget.geometry()))


def adjust_position(rect):
    """Adjust the given rect to ensure it's in the desktop space.

    :type rect: PyQt5.QtCore.QRect.QRect
    :return: PyQt5.QtCore.QRect.QRect
    """
    desktop = qApp.desktop().availableGeometry()

    if rect.bottom() > desktop.bottom():
        rect.moveTo(rect.x(), rect.y() - rect.height())
    if rect.right() > desktop.right():
        rect.moveTo(rect.x() - rect.width(), rect.y())

    return rect


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
        filters.append(key.title() + " (" + " *.".join(extensions[key]) + ")")

    filters.sort()

    if allexts:
        filters.insert(
            0, "All supported (" + " *.".join(chain(*extensions.values())) + ")"
        )
    if anyfile:
        filters.append("Any file (*)")

    return ";;".join(filters)


# Keep a reference of translators objects
_TRANSLATORS = []


def install_translation(name, tr_path=I18N_PATH):
    translator = QTranslator()
    translator.load(QLocale(), name, "_", tr_path)

    if QApplication.installTranslator(translator):
        # Keep a reference, QApplication does not
        _TRANSLATORS.append(translator)
        logger.debug(
            'Installed translation for "{}" from {}'.format(name, tr_path)
        )
    else:
        logger.debug('No translation for "{}" in {}'.format(name, tr_path))


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

    return sorted(iterable, key=tr_key, reverse=reverse)


class PyQtUnixSignalHandler:
    """
    Some magic horror to allow Python to execute signal handlers, this
    works only on posix systems where non-blocking anonymous pipe or socket are
    available.
    Can be used as a context manager, but after that is not reusable.

    From here: https://bitbucket.org/tortoisehg/thg/commits/550e1df5fbad
    """

    def __init__(self):
        # Create a non-blocking pipe
        self._rfd, self._wfd = os.pipe()
        for fd in (self._rfd, self._wfd):
            flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

        # QSocketNotifier will look if something is written in the pipe
        # and call the `_handle` method
        self._notifier = QSocketNotifier(self._rfd, QSocketNotifier.Read)
        self._notifier.activated.connect(self._handle)
        # Tell Python to write to the pipe when there is a signal to handle
        self._orig_wfd = signal.set_wakeup_fd(self._wfd)

    def release(self):
        # Stop the notifier
        self._notifier.setEnabled(False)
        # Restore the original descriptor
        signal.set_wakeup_fd(self._orig_wfd)

        # Cleanup
        self._orig_wfd = None
        os.close(self._rfd)
        os.close(self._wfd)

    def _handle(self):
        # Here Python signal handler will be invoked
        # We disable the notifier while doing so
        self._notifier.setEnabled(False)

        try:
            os.read(self._rfd, 1)
        except OSError:
            pass

        self._notifier.setEnabled(True)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
