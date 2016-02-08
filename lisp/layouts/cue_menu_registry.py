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

from PyQt5.QtWidgets import QAction, QMenu

from lisp.core.class_based_registry import ClassBasedRegistry
from lisp.cues.cue import Cue


class CueMenuRegistry(ClassBasedRegistry):

    def add_item(self, item, ref_class=Cue):
        if not isinstance(item, (QAction, QMenu)):
            raise TypeError('items must be QAction(s) or QMenu(s), not {0}'
                            .format(item.__class__.__name__))
        if not issubclass(ref_class, Cue):
            raise TypeError('ref_class must be Cue or a subclass, not {0}'
                            .format(ref_class.__name__))

        return super().add_item(item, ref_class)

    def add_separator(self, ref_class=Cue):
        """Register a separator menu-entry for ref_class and return it."""
        separator = QAction(None)
        separator.setSeparator(True)

        self.add_item(separator, ref_class)
        return separator

    def filter(self, ref_class=Cue):
        return super().filter(ref_class)

    def clear_class(self, ref_class=Cue):
        return super().filter(ref_class)
