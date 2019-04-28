# This file is part of Linux Show Player
#
# Copyright 2019 Francesco Ceruti <ceppofrancy@gmail.com>
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

from lisp.command.command import Command
from lisp.command.model import ModelInsertItemsCommand


class LayoutCommand(Command):
    __slots__ = ("_layout",)

    def __init__(self, layout):
        self._layout = layout


class LayoutAutoInsertCuesCommand(ModelInsertItemsCommand):
    def __init__(self, layout, *cues):
        # Insert after the current selection
        selection = tuple(layout.selected_cues())
        super().__init__(
            layout.model,
            selection[-1].index + 1 if selection else len(layout.model),
            *cues,
        )
