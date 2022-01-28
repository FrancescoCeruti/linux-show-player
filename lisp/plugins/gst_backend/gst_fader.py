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

from time import perf_counter_ns
from typing import Union

from lisp.core.fade_functions import ntime, FadeInType, FadeOutType
from lisp.core.fader import BaseFader


class GstFader(BaseFader):
    def __init__(self, target, attribute: str):
        super().__init__(target, attribute)
        self._start_time = -1

    def _fade(
        self,
        duration: float,
        to_value: float,
        fade_type: Union[FadeInType, FadeOutType],
    ) -> bool:
        base_value = getattr(self._target, self._attribute)
        value_diff = to_value - base_value

        if value_diff == 0:
            return True

        functor = fade_type.value
        steps = 100
        steps_duration = (duration * 1000) / steps
        control_points = {}

        for step in range(steps):
            control_points[step * steps_duration] = round(
                functor(
                    ntime(step, 0, steps - 1),
                    value_diff,
                    base_value,
                ),
                6,
            )

        controller = self._target.get_controller(self.attribute)
        controller.set(control_points)

        self._running.wait(controller.delay / 1000)

        self._start_time = perf_counter_ns()

        self._running.wait(duration)

    def _after_fade(self, interrupted):
        try:
            self._start_time = -1
            self._target.get_controller(self.attribute).reset()
        except Exception:
            pass

    def current_time(self):
        if self._start_time < 0:
            return 0

        return (perf_counter_ns() - self._start_time) // 1_000_000
