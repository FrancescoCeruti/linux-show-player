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

from abc import abstractmethod, ABC
from threading import Event
from typing import Union

from lisp.core.decorators import locked_method
from lisp.core.fade_functions import ntime, FadeInType, FadeOutType
from lisp.core.util import rsetattr, rgetattr, typename


class BaseFader(ABC):
    """Base class for "faders"

    * Works only for numeric attributes
    * When fading, the `fade` function cannot be entered by other threads,
      if this happens the function will simply return immediately
    * To execute a fader, the `prepare` function must be called first,
      this will also stop the fader
    * After calling `prepare` the fader is considered as running
    * The `stop` function wait until all "pending" target changes are applied
    * Changing the target will also stop the fader
    """

    def __init__(self, target, attribute: str):
        """
        :param target: The target object
        :param attribute: The target attribute (name) to be faded
        """
        self._target = target
        self._attribute = attribute

        self._is_ready = Event()
        self._is_ready.set()
        self._running = Event()
        self._running.set()

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, target):
        self.stop()
        self._target = target

    @property
    def attribute(self):
        return self._attribute

    @attribute.setter
    def attribute(self, attribute: str):
        self.stop()
        self._attribute = attribute

    @locked_method(blocking=False)
    def fade(
        self,
        duration: float,
        to_value: float,
        fade_type: Union[FadeInType, FadeOutType],
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

        try:
            self._fade(duration, to_value, fade_type)
        finally:
            interrupted = self._running.is_set()
            self._running.set()
            self._is_ready.set()

            self._after_fade(interrupted)

        return not interrupted

    def prepare(self):
        self.stop()

        self._running.clear()
        self._is_ready.clear()

    def stop(self):
        if not self._running.is_set():
            self._running.set()
            self._is_ready.wait()

    def is_running(self) -> bool:
        return not self._running.is_set()

    def _after_fade(self, interrupted):
        pass

    @abstractmethod
    def _fade(
        self,
        duration: float,
        to_value: float,
        fade_type: Union[FadeInType, FadeOutType],
    ) -> bool:
        pass

    @abstractmethod
    def current_time(self) -> int:
        """Fader running time, in milliseconds"""
        pass


class DummyFader(BaseFader):
    def __init__(self):
        super().__init__(None, "")

    def _fade(
        self,
        duration: float,
        to_value: float,
        fade_type: Union[FadeInType, FadeOutType],
    ) -> bool:
        return True

    def current_time(self) -> int:
        return 0


class Fader(BaseFader):
    """Perform fades on "generic" objects attributes.

    * Fades have a resolution of `1-hundredth-of-second`
    """

    def __init__(self, target, attribute):
        super().__init__(target, attribute)
        # current fade time in hundredths-of-seconds
        self._time = 0

    def _fade(
        self,
        duration: float,
        to_value: float,
        fade_type: Union[FadeInType, FadeOutType],
    ) -> bool:
        self._time = 0

        begin = 0
        functor = fade_type.value
        duration = int(duration * 100)
        base_value = rgetattr(self._target, self._attribute)
        value_diff = to_value - base_value

        if value_diff == 0:
            return True

        while self._time <= duration and not self._running.is_set():
            rsetattr(
                self._target,
                self._attribute,
                round(
                    functor(
                        ntime(self._time, begin, duration),
                        value_diff,
                        base_value,
                    ),
                    6,
                ),
            )

            self._time += 1
            self._running.wait(0.01)

    def _after_fade(self, interrupted):
        self._time = 0

    def current_time(self) -> int:
        return round(self._time * 10)
