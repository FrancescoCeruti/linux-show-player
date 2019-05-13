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

from threading import Event

from lisp.core.decorators import locked_method
from lisp.core.fade_functions import ntime, FadeInType, FadeOutType
from lisp.core.util import rsetattr, rgetattr, typename


class Fader:
    """Allow to perform fades on "generic" objects attributes.

     * Fades have a resolution of `1-hundredth-of-second`
     * To be able to fade correctly the attribute must be numeric, if not, the
       `fade` function will fail
     * When fading, the `fade` function cannot be entered by other threads,
       if this happens the function will simply return immediately
     * To execute a fader, the `prepare` function must be called first,
       this will also stop the fader
     * After calling `prepare` the fader is considered as running
     * The `stop` function wait until all "pending" target changes are applied
     * Changing the target will also stop the fader
    """

    def __init__(self, target, attribute):
        """
        :param target: The target object
        :type target: object
        :param attribute: The target attribute (name) to be faded
        :type attribute: str
        """
        self._time = 0  # current fade time in hundredths-of-seconds
        self._target = target
        self._attribute = attribute

        self._is_ready = Event()
        self._is_ready.set()
        self._running = Event()
        self._running.set()
        self._pause = Event()
        self._pause.set()

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
    def attribute(self, target_property):
        self.stop()
        self._attribute = target_property

    def prepare(self):
        self.stop()

        self._running.clear()
        self._is_ready.clear()

    @locked_method(blocking=False)
    def fade(self, duration, to_value, fade_type):
        """
        :param duration: How much the fade should be long (in seconds)
        :type duration: float
        :param to_value: The value to reach
        :type to_value: float
        :param fade_type: The fade type
        :type fade_type: FadeInType | FadeOutType

        :return: False if the fade as been interrupted, True otherwise
        :rtype: bool
        """
        if duration <= 0:
            return

        if not isinstance(fade_type, (FadeInType, FadeOutType)):
            raise AttributeError(
                "fade_type must be one of FadeInType or FadeOutType members,"
                "not {}".format(typename(fade_type))
            )

        try:
            self._time = 0
            begin = 0
            functor = fade_type.value
            duration = int(duration * 100)
            base_value = rgetattr(self._target, self._attribute)
            value_diff = to_value - base_value

            if value_diff == 0:
                return

            while self._time <= duration and not self._running.is_set():
                rsetattr(
                    self._target,
                    self._attribute,
                    functor(
                        ntime(self._time, begin, duration),
                        value_diff,
                        base_value,
                    ),
                )

                self._time += 1
                self._running.wait(0.01)
                self._pause.wait()
        finally:
            interrupted = self._running.is_set()
            self._running.set()
            self._is_ready.set()
            self._time = 0

        return not interrupted

    def stop(self):
        if not self._running.is_set() or not self._pause.is_set():
            self._running.set()
            self._pause.set()
            self._is_ready.wait()

    def pause(self):
        if self.is_running():
            self._pause.clear()

    def resume(self):
        self._pause.set()

    def is_paused(self):
        return not self._pause.is_set()

    def is_running(self):
        return not self._running.is_set() and not self.is_paused()

    def current_time(self):
        # Return the time in millisecond
        return self._time * 10
