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

from PyQt5.QtWidgets import QStyledItemDelegate, QSpinBox, QDoubleSpinBox


class OscArgumentDelegate(QStyledItemDelegate):
    NUMERIC_MIN = -1_000_000
    NUMERIC_MAX = 1_000_000
    FLOAT_DECIMALS = 3

    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)

        if isinstance(editor, QSpinBox):
            editor.setRange(self.NUMERIC_MIN, self.NUMERIC_MAX)
            editor.setSingleStep(1)
        elif isinstance(editor, QDoubleSpinBox):
            editor.setRange(self.NUMERIC_MIN, self.NUMERIC_MAX)
            editor.setDecimals(self.FLOAT_DECIMALS)
            editor.setSingleStep(0.01)

        return editor
