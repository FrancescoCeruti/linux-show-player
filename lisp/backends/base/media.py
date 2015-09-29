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

from abc import abstractmethod, ABCMeta
from enum import Enum

from lisp.core.has_properties import HasProperties
from lisp.core.signal import Signal


class MediaState(Enum):
    """Media status: identify the current media state"""
    Error = -1
    Null = 0
    Playing = 1
    Paused = 2
    Stopped = 3


# TODO: detailed Media docs
class Media(HasProperties, metaclass=ABCMeta):
    """Media(s) provides control over some kind of multimedia object

    """

    def __init__(self):
        super().__init__()

        #: Current state
        self.state = MediaState.Null

        #: Emitted when paused (self)
        self.paused = Signal()
        #: Emitted when played (self)
        self.played = Signal()
        #: Emitted when stopped (self)
        self.stopped = Signal()
        #: Emitted after interruption (self)
        self.interrupted = Signal()
        #: End-of-Stream (self)
        self.eos = Signal()

        #: Emitted before play (self)
        self.on_play = Signal()
        #: Emitted before stop (self)
        self.on_stop = Signal()
        #: Emitted before pause (self)
        self.on_pause = Signal()

        #: Emitted after a seek (self, position)
        self.sought = Signal()
        #: Emitted when an error occurs (self, error, details)
        self.error = Signal()

    @abstractmethod
    def current_time(self):
        """
        :return: the current playback time in milliseconds or -1
        :rtype: int
        """

    @abstractmethod
    def element(self, name):
        """
        :param name: The element name
        :type name: str

        :return: The element with the specified name or None
        :rtype: lisp.core.base.media_element.MediaElement
        """

    @abstractmethod
    def elements(self):
        """
        :return: All the MediaElement(s) of the media
        :rtype: list
        """

    @abstractmethod
    def elements_properties(self):
        """
        :return: Elements configuration
        :rtype: dict
        """

    @abstractmethod
    def input_uri(self):
        """
        :return: The media input uri (e.g. "file:///home/..."), or None
        :rtype: str
        """

    @abstractmethod
    def interrupt(self):
        """Stop the playback without effects, go in STOPPED state and emit
        the interrupted signal
        """

    @abstractmethod
    def pause(self):
        """The media go in PAUSED state and pause the playback

        """

    @abstractmethod
    def play(self):
        """The media go in PLAYING state and starts the playback

        """

    @abstractmethod
    def seek(self, position):
        """Seek to the specified point

        :param position: The position to be reached
        :type position: int

        """

    @abstractmethod
    def stop(self):
        """The media go in STOPPED state and stop the playback

        """

    @abstractmethod
    def update_elements(self, settings):
        """Update the elements configuration

        :param settings: Media-elements settings
        :type settings: dict
        """