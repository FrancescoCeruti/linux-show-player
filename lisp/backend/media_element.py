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

from enum import Enum

from lisp.core.has_properties import HasProperties


class ElementType(Enum):
    """The type of the media-element"""
    Input = 0
    Output = 1
    Plugin = 2


class MediaType(Enum):
    """The media-type that the element handle (Audio/Video)"""
    Audio = 0
    Video = 1
    AudioAndVideo = 2


class MediaElement(HasProperties):
    """Base media-element class

    A MediaElement object control specific media's parameters (e.g. volume).
    Every MediaElement provides two kind of properties:
     1) The one defined via class:`HasProperties`;
     2) runtime only properties, those are reset to the previous value at
        playback end.

    Runtime properties are defined using the following naming convention:
    runtime_<property_name>.
    """

    ElementType = None
    MediaType = None
    Name = 'Undefined'
