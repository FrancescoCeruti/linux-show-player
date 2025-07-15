# This file is part of Linux Show Player
#
# Copyright 2017 Francesco Ceruti <ceppofrancy@gmail.com>
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

from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from typing import Iterable

from lisp.core.decorators import locked_method
from lisp.core.fader import BaseFader
from lisp.core.fade_functions import FadeInType, FadeOutType
from lisp.core.util import typename


class FaderGroup:
    _faders: "list[BaseFader]" = []

    def __init__(self, faders: "list[BaseFader]" = []):
        """
        :param faders: The faders of this FaderGroup
        """
        self._faders = faders.copy()

    def add_fader(self, fader: "BaseFader") -> bool:
        """
        :param fader: the fader to add

        :return: False if fader is already part of Group, True otherwise
        """
        if fader in self._faders:
            return False
        self._faders.append(fader)
        return True

    def rem_fader(self, fader: "BaseFader") -> bool:
        """
        :param fader: the fader to remove

        :return: False if fader not in group, True otherwise
        """
        if fader not in self._faders:
            return False
        self._faders.remove(fader)
        return True

    def clear(self):
        self._faders.clear()

    def __len__(self):
        return len(self._faders)

    @locked_method(blocking=False)
    def fade(
        self,
        duration: float,
        to_value: "float | list[float]",
        fade_type: "FadeInType | FadeOutType"
    ) -> bool:
        """
        :param duration: How much the fade should be long (in seconds)
        :param to_value: The value to reach
        :param fade_type: The fade type

        :return: False if the fade as been interrupted, True otherwise
        """
        if duration <= 0:
            return True

        if not isinstance(fade_type, (FadeInType, FadeOutType)):
            raise AttributeError(
                "fade_type must be one of FadeInType or FadeOutType members,"
                f"not {typename(fade_type)}"
            )

        if not isinstance(to_value, Iterable):
            to_value = [to_value] * len(self._faders)

        if len(to_value) != len(self._faders):
            raise AttributeError(
                "to_value must have the same number of values as faders in the group,"
                f"was: {len(to_value)}, should_be: {len(self._faders)}"
            )

        with ThreadPoolExecutor(len(self._faders), "fade") as executor:
            futures: 'list[Future]' = []
            for fader, value in zip(self._faders, to_value):
                futures.append(executor.submit(fader.fade, duration, value, fade_type))

            for future in as_completed(futures):
                if not future.result():
                    return False
        return True

    def prepare(self):
        for fader in self._faders:
            fader.prepare()

    def stop(self):
        for fader in self._faders:
            fader.stop()

    def is_running(self) -> bool:
        return any(fader.is_running() for fader in self._faders)
