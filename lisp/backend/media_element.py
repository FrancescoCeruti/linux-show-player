# This file is part of Linux Show Player
#
# Copyright 2024 Francesco Ceruti <ceppofrancy@gmail.com>
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
from typing import Optional

from lisp.core.fader import BaseFader
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
    Unknown = 4


class MediaElement(HasProperties):
    """Base media-element class

    A MediaElement object control specific media's parameters (e.g. volume).
    """

    ElementType = None
    MediaType = None
    Name = "Undefined"

    def get_fader(self, property_name: str) -> Optional[BaseFader]:
        """Get the appropriate fader object for the given property."""
        return None
