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

from PyQt5.QtWidgets import QTimeEdit


class QStepTimeEdit(QTimeEdit):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        self._sections_steps = {}

    def setSectionStep(self, section, step):
        if not isinstance(section, QTimeEdit.Section):
            raise AttributeError("Not a QTimeEdit.Section")
        if step <= 0:
            raise AttributeError("Step value must be >= 0")

        self._sections_steps[section] = step

    def stepBy(self, value):
        step = self._sections_steps.get(self.currentSection(), 1)

        if abs(value) != step:
            sign = 1 if value >= 0 else -1
            value = sign * step

        super().stepBy(value)
