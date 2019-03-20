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

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP, QTimer
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QAction

from lisp.core.configuration import DummyConfiguration
from lisp.core.properties import ProxyProperty
from lisp.core.signal import Connection
from lisp.cues.cue import Cue, CueAction, CueNextAction
from lisp.cues.cue_factory import CueFactory
from lisp.cues.cue_memento_model import CueMementoAdapter
from lisp.layout.cue_layout import CueLayout
from lisp.layout.cue_menu import (
    SimpleMenuAction,
    MENU_PRIORITY_CUE,
    MenuActionsGroup,
)
from lisp.plugins.list_layout.list_view import CueListView
from lisp.plugins.list_layout.models import CueListModel, RunningCueModel
from lisp.plugins.list_layout.view import ListLayoutView
from lisp.ui.ui_utils import translate


class ListLayout(CueLayout):
    NAME = QT_TRANSLATE_NOOP("LayoutName", "List Layout")
    DESCRIPTION = QT_TRANSLATE_NOOP(
        "LayoutDescription", "Organize the cues in a list"
    )
    DETAILS = [
        QT_TRANSLATE_NOOP(
            "LayoutDetails", "SHIFT + Space or Double-Click to edit a cue"
        ),
        QT_TRANSLATE_NOOP(
            "LayoutDetails", "To copy cues drag them while pressing CTRL"
        ),
        QT_TRANSLATE_NOOP("LayoutDetails", "To move cues drag them"),
    ]
    Config = DummyConfiguration()

    auto_continue = ProxyProperty()
    running_visible = ProxyProperty()
    dbmeters_visible = ProxyProperty()
    seek_sliders_visible = ProxyProperty()
    accurate_time = ProxyProperty()
    selection_mode = ProxyProperty()

    def __init__(self, application):
        super().__init__(application)
        self._list_model = CueListModel(self.cue_model)
        self._list_model.item_added.connect(self.__cue_added)
        self._memento_model = CueMementoAdapter(self._list_model)
        self._running_model = RunningCueModel(self.cue_model)
        self._go_timer = QTimer()
        self._go_timer.setSingleShot(True)

        self._view = ListLayoutView(
            self._list_model, self._running_model, self.Config
        )
        # GO button
        self._view.goButton.clicked.connect(self.__go_slot)
        # Global actions
        self._view.controlButtons.stopButton.clicked.connect(self.stop_all)
        self._view.controlButtons.pauseButton.clicked.connect(self.pause_all)
        self._view.controlButtons.fadeInButton.clicked.connect(self.fadein_all)
        self._view.controlButtons.fadeOutButton.clicked.connect(
            self.fadeout_all
        )
        self._view.controlButtons.resumeButton.clicked.connect(self.resume_all)
        self._view.controlButtons.interruptButton.clicked.connect(
            self.interrupt_all
        )
        # Cue list
        self._view.listView.itemDoubleClicked.connect(self._double_clicked)
        self._view.listView.contextMenuInvoked.connect(self._context_invoked)
        self._view.listView.keyPressed.connect(self._key_pressed)

        # Layout menu
        layout_menu = self.app.window.menuLayout

        self.show_running_action = QAction(parent=layout_menu)
        self.show_running_action.setCheckable(True)
        self.show_running_action.triggered.connect(self._set_running_visible)
        layout_menu.addAction(self.show_running_action)

        self.show_dbmeter_action = QAction(parent=layout_menu)
        self.show_dbmeter_action.setCheckable(True)
        self.show_dbmeter_action.triggered.connect(self._set_dbmeters_visible)
        layout_menu.addAction(self.show_dbmeter_action)

        self.show_seek_action = QAction(parent=layout_menu)
        self.show_seek_action.setCheckable(True)
        self.show_seek_action.triggered.connect(self._set_seeksliders_visible)
        layout_menu.addAction(self.show_seek_action)

        self.show_accurate_action = QAction(parent=layout_menu)
        self.show_accurate_action.setCheckable(True)
        self.show_accurate_action.triggered.connect(self._set_accurate_time)
        layout_menu.addAction(self.show_accurate_action)

        self.auto_continue_action = QAction(parent=layout_menu)
        self.auto_continue_action.setCheckable(True)
        self.auto_continue_action.triggered.connect(self._set_auto_continue)
        layout_menu.addAction(self.auto_continue_action)

        self.selection_mode_action = QAction(parent=layout_menu)
        self.selection_mode_action.setCheckable(True)
        self.selection_mode_action.triggered.connect(self._set_selection_mode)
        self.selection_mode_action.setShortcut(QKeySequence("Ctrl+Alt+S"))
        layout_menu.addAction(self.selection_mode_action)

        # Load settings
        self._go_key_sequence = QKeySequence(
            ListLayout.Config["goKey"], QKeySequence.NativeText
        )
        self._set_seeksliders_visible(ListLayout.Config["show.seekSliders"])
        self._set_running_visible(ListLayout.Config["show.playingCues"])
        self._set_accurate_time(ListLayout.Config["show.accurateTime"])
        self._set_dbmeters_visible(ListLayout.Config["show.dBMeters"])
        self._set_selection_mode(ListLayout.Config["selectionMode"])
        self._set_auto_continue(ListLayout.Config["autoContinue"])

        # Context menu actions
        self._edit_actions_group = MenuActionsGroup(priority=MENU_PRIORITY_CUE)
        self._edit_actions_group.add(
            SimpleMenuAction(
                translate("ListLayout", "Edit cue"),
                self.edit_cue,
                translate("ListLayout", "Edit selected"),
                self.edit_cues,
            ),
            SimpleMenuAction(
                translate("ListLayout", "Clone cue"),
                self._clone_cue,
                translate("ListLayout", "Clone selected"),
                self._clone_cues,
            ),
            SimpleMenuAction(
                translate("ListLayout", "Remove cue"),
                self.cue_model.remove,
                translate("ListLayout", "Remove selected"),
                self._remove_cues,
            ),
        )

        self.CuesMenu.add(self._edit_actions_group)

        self.retranslate()

    def retranslate(self):
        self.show_running_action.setText(
            translate("ListLayout", "Show playing cues")
        )
        self.show_dbmeter_action.setText(
            translate("ListLayout", "Show dB-meters")
        )
        self.show_seek_action.setText(translate("ListLayout", "Show seek-bars"))
        self.show_accurate_action.setText(
            translate("ListLayout", "Show accurate time")
        )
        self.auto_continue_action.setText(
            translate("ListLayout", "Auto-select next cue")
        )
        self.selection_mode_action.setText(
            translate("ListLayout", "Selection mode")
        )

    def cues(self, cue_type=Cue):
        yield from self._list_model

    def view(self):
        return self._view

    def standby_index(self):
        return self._view.listView.standbyIndex()

    def set_standby_index(self, index):
        self._view.listView.setStandbyIndex(index)

    def go(self, action=CueAction.Default, advance=1):
        standby_cue = self.standby_cue()
        if standby_cue is not None:
            standby_cue.execute(action)
            self.cue_executed.emit(standby_cue)

            if self.auto_continue:
                self.set_standby_index(self.standby_index() + advance)

    def cue_at(self, index):
        return self._list_model.item(index)

    def selected_cues(self, cue_type=Cue):
        for item in self._view.listView.selectedItems():
            yield self._list_model.item(
                self._view.listView.indexOfTopLevelItem(item)
            )

    def finalize(self):
        # Clean layout menu
        self.app.window.menuLayout.clear()
        # Clean context-menu
        self.CuesMenu.remove(self._edit_actions_group)
        # Remove reference cycle
        del self._edit_actions_group

    def select_all(self, cue_type=Cue):
        if self.selection_mode:
            for index in range(self._view.listView.topLevelItemCount()):
                if isinstance(self._list_model.item(index), cue_type):
                    self._view.listView.topLevelItem(index).setSelected(True)

    def deselect_all(self, cue_type=Cue):
        for index in range(self._view.listView.topLevelItemCount()):
            if isinstance(self._list_model.item(index), cue_type):
                self._view.listView.topLevelItem(index).setSelected(False)

    def invert_selection(self):
        if self.selection_mode:
            for index in range(self._view.listView.topLevelItemCount()):
                item = self._view.listView.topLevelItem(index)
                item.setSelected(not item.isSelected())

    def _key_pressed(self, event):
        event.ignore()

        if not event.isAutoRepeat():
            keys = event.key()
            modifiers = event.modifiers()

            if modifiers & Qt.ShiftModifier:
                keys += Qt.SHIFT
            if modifiers & Qt.ControlModifier:
                keys += Qt.CTRL
            if modifiers & Qt.AltModifier:
                keys += Qt.ALT
            if modifiers & Qt.MetaModifier:
                keys += Qt.META

            sequence = QKeySequence(keys)
            if sequence in self._go_key_sequence:
                event.accept()
                self.__go_slot()
            elif sequence == QKeySequence.Delete:
                self._remove_cues(self.selected_cues())
            elif event.key() == Qt.Key_Space:
                if event.modifiers() == Qt.ShiftModifier:
                    event.accept()

                    cue = self.standby_cue()
                    if cue is not None:
                        self.edit_cue(cue)
            else:
                self.key_pressed.emit(event)
                event.ignore()

    @accurate_time.set
    def _set_accurate_time(self, accurate):
        self.show_accurate_action.setChecked(accurate)
        self._view.runView.accurate_time = accurate

    @accurate_time.get
    def _get_accurate_time(self):
        return self.show_accurate_action.isChecked()

    @auto_continue.set
    def _set_auto_continue(self, enable):
        self.auto_continue_action.setChecked(enable)

    @auto_continue.get
    def _get_auto_select_next(self):
        return self.auto_continue_action.isChecked()

    @seek_sliders_visible.set
    def _set_seeksliders_visible(self, visible):
        self.show_seek_action.setChecked(visible)
        self._view.runView.seek_visible = visible

    @seek_sliders_visible.get
    def _get_seeksliders_visible(self):
        return self.show_seek_action.isChecked()

    @dbmeters_visible.set
    def _set_dbmeters_visible(self, visible):
        self.show_dbmeter_action.setChecked(visible)
        self._view.runView.dbmeter_visible = visible

    @dbmeters_visible.get
    def _get_dbmeters_visible(self):
        return self.show_dbmeter_action.isChecked()

    @running_visible.set
    def _set_running_visible(self, visible):
        self.show_running_action.setChecked(visible)
        self._view.runView.setVisible(visible)
        self._view.controlButtons.setVisible(visible)

    @running_visible.get
    def _get_running_visible(self):
        return self.show_running_action.isChecked()

    @selection_mode.set
    def _set_selection_mode(self, enable):
        self.selection_mode_action.setChecked(enable)
        if enable:
            self._view.listView.setSelectionMode(CueListView.ExtendedSelection)

            standby = self.standby_index()
            if standby >= 0:
                self._view.listView.topLevelItem(standby).setSelected(True)
        else:
            self.deselect_all()
            self._view.listView.setSelectionMode(CueListView.NoSelection)

    @selection_mode.get
    def _get_selection_mode(self):
        return self.selection_mode_action.isChecked()

    def _double_clicked(self):
        cue = self.standby_cue()
        if cue is not None:
            self.edit_cue(cue)

    def _context_invoked(self, event):
        # This is called in response to CueListView context-events
        if self._view.listView.itemAt(event.pos()) is not None:
            cues = list(self.selected_cues())
            if not cues:
                context_index = self._view.listView.indexAt(event.pos())
                if context_index.isValid():
                    cues.append(self._list_model.item(context_index.row()))
                else:
                    return

            self.show_cue_context_menu(cues, event.globalPos())
        else:
            self.show_context_menu(event.globalPos())

    def _clone_cue(self, cue):
        self._clone_cues((cue,))

    def _clone_cues(self, cues):
        for pos, cue in enumerate(cues, cues[-1].index + 1):
            clone = CueFactory.clone_cue(cue)
            clone.name = "Copy of {}".format(clone.name)
            self._list_model.insert(clone, pos)

    def __go_slot(self):
        if not self._go_timer.isActive():
            action = CueAction(ListLayout.Config.get("goAction"))
            self.go(action=action)

            self._go_timer.setInterval(ListLayout.Config.get("goDelay"))
            self._go_timer.start()

    def __cue_added(self, cue):
        cue.next.connect(self.__cue_next, Connection.QtQueued)

    def __cue_next(self, cue):
        try:
            next_index = cue.index + 1
            if next_index < len(self._list_model):
                action = CueNextAction(cue.next_action)
                if (
                    action == CueNextAction.SelectAfterEnd
                    or action == CueNextAction.SelectAfterWait
                ):
                    self.set_standby_index(next_index)
                else:
                    next_cue = self._list_model.item(next_index)
                    next_cue.execute()

                    if self.auto_continue and next_cue is self.standby_cue():
                        self.set_standby_index(next_index + 1)
        except (IndexError, KeyError):
            pass
