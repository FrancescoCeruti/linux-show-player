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

from functools import partial

from PyQt5.QtWidgets import QAction, QMenu

from lisp.core.class_based_registry import ClassBasedRegistry
from lisp.core.util import greatest_common_superclass
from lisp.cues.cue import Cue

MENU_PRIORITY_CUE = 0
MENU_PRIORITY_LAYOUT = 100
MENU_PRIORITY_PLUGIN = 1000
MENU_PRIORITY_NONE = float("inf")


class MenuAction:
    def __init__(self, priority=MENU_PRIORITY_NONE):
        self.priority = priority

    def show(self, cues):
        return False

    def text(self, cues):
        pass

    def action(self, cues):
        pass


class SimpleMenuAction(MenuAction):
    def __init__(self, s_text, s_action, m_text=None, m_action=None, **kwargs):
        super().__init__(**kwargs)
        self._s_text = s_text
        self._s_action = s_action
        self._m_text = m_text
        self._m_action = m_action

    def show(self, cues):
        return not (
            len(cues) > 1 and (self._m_text is None or self._m_action is None)
        )

    def text(self, cues):
        if len(cues) == 1:
            return self._s_text
        elif len(cues) > 1:
            return self._m_text

    def action(self, cues):
        if len(cues) == 1:
            return self._s_action(cues[0])
        elif len(cues) > 1:
            return self._m_action(cues)


class MenuActionsGroup:
    def __init__(
        self,
        separators=True,
        submenu=False,
        text="",
        priority=MENU_PRIORITY_NONE,
    ):
        """
        :param separators: if True a separator is put before and after the group
        :param submenu: if True the actions are put in a submenu
        :param text: the text to use when `submenu` is True
        :param priority: the group priority, same as `MenuAction`
        """

        self.submenu = submenu
        self.separators = separators
        self.priority = priority
        self.text = text

        self.actions = []

    def add(self, *actions):
        self.actions.extend(actions)

    def remove(self, action):
        self.actions.remove(action)


def create_qmenu(actions, cues, menu):
    for action in sorted(actions, key=lambda a: a.priority):
        if isinstance(action, MenuActionsGroup):
            if action.separators:
                menu.addSeparator()

            if action.submenu:
                menu.addMenu(
                    create_qmenu(
                        action.actions, cues, QMenu(action.text, parent=menu)
                    )
                )
            else:
                create_qmenu(action.actions, cues, menu)

            if action.separators:
                menu.addSeparator()

        elif action.show(cues):
            qaction = QAction(action.text(cues), parent=menu)
            qaction.triggered.connect(partial(action.action, cues))
            menu.addAction(qaction)

    return menu


class CueContextMenu(ClassBasedRegistry):
    def add(self, item, ref_class=Cue):
        """
        :type item: typing.Union[MenuAction, MenuActionGroup]
        """
        if not isinstance(item, (MenuAction, MenuActionsGroup)):
            raise TypeError()

        if not issubclass(ref_class, Cue):
            raise TypeError(
                "ref_class must be Cue or a subclass, not {0}".format(
                    ref_class.__name__
                )
            )

        super().add(item, ref_class)

    def filter(self, ref_class=Cue):
        return super().filter(ref_class)

    def clear_class(self, ref_class=Cue):
        return super().filter(ref_class)

    def create_qmenu(self, cues, parent):
        ref_class = greatest_common_superclass(cues)
        return create_qmenu(self.filter(ref_class), cues, QMenu(parent))
