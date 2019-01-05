# This file is part of Linux Show Player
#
# Copyright 2018 Francesco Ceruti <ceppofrancy@gmail.com>
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

from abc import abstractmethod
from enum import Enum

from lisp.core.has_properties import HasProperties
from lisp.core.properties import Property
from lisp.core.signal import Signal


class MediaState(Enum):
    """Identify the current media state"""

    Null = 0
    Playing = 1
    Paused = 2
    Ready = 3


class Media(HasProperties):
    """Interface for Media objects.

    Media(s) provides control over multimedia contents.
    To control various parameter of the media, MediaElement(s) should be used.

    .. note::
        The play/stop/pause functions must be non-blocking functions.
    """

    loop = Property(default=0)
    duration = Property(default=0)
    start_time = Property(default=0)
    stop_time = Property(default=0)
    elements = Property(default={})

    def __init__(self):
        super().__init__()

        self.paused = Signal()
        # Emitted when paused (self)
        self.played = Signal()
        # Emitted when played (self)
        self.stopped = Signal()
        # Emitted when stopped (self)
        self.eos = Signal()
        # End-of-Stream (self)

        self.on_play = Signal()
        # Emitted before play (self)
        self.on_stop = Signal()
        # Emitted before stop (self)
        self.on_pause = Signal()
        # Emitted before pause (self)

        self.sought = Signal()
        # Emitted after a seek (self, position)
        self.error = Signal()
        # Emitted when an error occurs (self)

        self.elements_changed = Signal()
        # Emitted when one or more elements are added/removed (self)

    @property
    @abstractmethod
    def state(self):
        """
        :return: the media current state
        :rtype: MediaState
        """

    @abstractmethod
    def current_time(self):
        """
        :return: the current playback time in milliseconds or 0
        :rtype: int
        """

    @abstractmethod
    def element(self, class_name):
        """
        :param class_name: The element class-name
        :type class_name: str

        :return: The element with the specified class-name or None
        :rtype: lisp.core.base.media_element.MediaElement
        """

    @abstractmethod
    def input_uri(self):
        """
        :return: The media input uri (e.g. "file:///home/..."), or None
        :rtype: str
        """

    @abstractmethod
    def pause(self):
        """The media go in PAUSED state (pause the playback)."""

    @abstractmethod
    def play(self):
        """The media go in PLAYING state (starts the playback)."""

    @abstractmethod
    def seek(self, position):
        """Seek to the specified point.

        :param position: The position to be reached in milliseconds
        :type position: int
        """

    @abstractmethod
    def stop(self):
        """The media go in READY state (stop the playback)."""
