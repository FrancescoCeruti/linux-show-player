# This file is part of Linux Show Player
#
# Copyright 2023 Francesco Ceruti <ceppofrancy@gmail.com>
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

from abc import abstractmethod, ABC

from lisp.backend.audio_utils import iec_scale


class Scale(ABC):
    min: int
    max: int

    @abstractmethod
    def scale(self, value):
        pass


class IECScale(Scale):
    min: int = -70
    max: int = 0

    def scale(self, value):
        return iec_scale(value)


class LinearScale(Scale):
    min: int = -60
    max: int = 0

    def scale(self, value):
        if value < self.min:
            return 0
        elif value < self.max:
            return 1 + (value / (abs(self.min) + abs(self.max)))

        return 1
