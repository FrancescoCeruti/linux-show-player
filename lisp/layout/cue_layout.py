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

from abc import abstractmethod

from lisp.core.actions_handler import MainActionsHandler
from lisp.core.has_properties import HasProperties
from lisp.core.signal import Signal
from lisp.core.util import greatest_common_superclass
from lisp.cues.cue import Cue, CueAction
from lisp.cues.cue_actions import UpdateCueAction, UpdateCuesAction
from lisp.layout.cue_menu import CueContextMenu
from lisp.ui.settings.cue_settings import CueSettingsDialog
from lisp.ui.ui_utils import adjust_widget_position


class CueLayout(HasProperties):
    # Layout name
    NAME = "Base"
    # Layout short description
    DESCRIPTION = "No description"
    # Layout details (some useful info)
    DETAILS = ""

    CuesMenu = CueContextMenu()

    def __init__(self, application):
        """
        :type application: lisp.application.Application
        """
        super().__init__()
        self.app = application

        self.cue_executed = Signal()  # After a cue is executed
        self.all_executed = Signal()  # After execute_all is called

        # TODO: self.standby_changed = Signal()
        self.key_pressed = Signal()  # After a key is pressed

    @property
    def cue_model(self):
        """:rtype: lisp.cues.cue_model.CueModel"""
        return self.app.cue_model

    @abstractmethod
    def view(self):
        """:rtype: PyQt5.QtWidgets.QWidget"""

    @abstractmethod
    def cues(self, cue_type=Cue):
        """Iterator over the cues, ordered (by index) and filtered by type.

        :param cue_type: the "minimum" type of the cue
        :type cue_type: type

        :rtype: typing.Iterable[Cue]
        """

    @abstractmethod
    def cue_at(self, index):
        """Return the cue at the given index, or raise IndexError

        :rtype: Cue
        """

    def standby_cue(self):
        """Return the standby cue, or None.

        :rtype: Cue
        """
        try:
            return self.cue_at(self.standby_index())
        except IndexError:
            return None

    def standby_index(self):
        """Return the standby index, or -1."""
        return -1

    def set_standby_index(self, index):
        """Set the current index"""

    @abstractmethod
    def selected_cues(self, cue_type=Cue):
        """Iterate the selected cues, filtered by type.

        :param cue_type: the "minimum" type of the cue
        :type cue_type: type
        :rtype: typing.Iterable
        """

    @abstractmethod
    def invert_selection(self):
        """Invert selection"""

    @abstractmethod
    def select_all(self, cue_type=Cue):
        """Select all the cues of type `cue_type`

        :param cue_type: the "minimum" type of the cue of the item to select.
        """

    @abstractmethod
    def deselect_all(self, cue_type=Cue):
        """Deselect all the cues of type `cue_type`

        :param cue_type: the "minimum" type of the cue of the item to deselect.
        """

    def go(self, action=CueAction.Default, advance=1):
        """Execute the current cue and go ahead.

        .. Note::
            The advance value can be ignored by the layout.

        :param action: the action the cue should execute
        :param advance: number of index to advance (with negative will go back)
        :rtype: lisp.cues.cue.Cue
        """

    def execute_all(self, action, quiet=False):
        """Execute the given action on all the layout cues

        :param action: The action to be executed
        :type action: CueAction
        :param quiet: If True `all_executed` is not emitted
        :type quiet: bool
        """
        for cue in self.cues():
            cue.execute(action)

        if not quiet:
            self.all_executed.emit(action)

    def stop_all(self):
        if self.app.conf.get("layout.stopAllFade", False):
            self.execute_all(CueAction.FadeOutStop)
        else:
            self.execute_all(CueAction.Stop)

    def interrupt_all(self):
        if self.app.conf.get("layout.interruptAllFade", False):
            self.execute_all(CueAction.FadeOutInterrupt)
        else:
            self.execute_all(CueAction.Interrupt)

    def pause_all(self):
        if self.app.conf.get("layout.pauseAllFade", False):
            self.execute_all(CueAction.FadeOutPause)
        else:
            self.execute_all(CueAction.Pause)

    def resume_all(self):
        if self.app.conf.get("layout.resumeAllFade", True):
            self.execute_all(CueAction.FadeInResume)
        else:
            self.execute_all(CueAction.Resume)

    def fadein_all(self):
        self.execute_all(CueAction.FadeIn)

    def fadeout_all(self):
        self.execute_all(CueAction.FadeOut)

    def edit_cue(self, cue):
        dialog = CueSettingsDialog(cue, parent=self.app.window)

        def on_apply(settings):
            action = UpdateCueAction(settings, cue)
            MainActionsHandler.do_action(action)

        dialog.onApply.connect(on_apply)
        dialog.exec()

    def edit_cues(self, cues):
        if cues:
            # Use the greatest common superclass between the selected cues
            dialog = CueSettingsDialog(
                greatest_common_superclass(cues), parent=self.app.window
            )

            def on_apply(settings):
                action = UpdateCuesAction(settings, cues)
                MainActionsHandler.do_action(action)

            dialog.onApply.connect(on_apply)
            dialog.exec()

    def show_context_menu(self, position):
        menu = self.app.window.menuEdit
        menu.move(position)
        menu.show()

        adjust_widget_position(menu)

    def show_cue_context_menu(self, cues, position):
        if cues:
            menu = self.CuesMenu.create_qmenu(cues, self.view())
            menu.move(position)
            menu.show()

            adjust_widget_position(menu)

    def finalize(self):
        """Destroy all the layout elements"""

    def _remove_cue(self, cue):
        self.cue_model.remove(cue)

    def _remove_cues(self, cues):
        for cue in cues:
            self.cue_model.remove(cue)
