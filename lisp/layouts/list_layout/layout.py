# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2017 Francesco Ceruti <ceppofrancy@gmail.com>
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

from enum import Enum

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QWidget, QAction, qApp, QGridLayout, \
    QPushButton, QSizePolicy

from lisp.core.configuration import config
from lisp.core.signal import Connection
from lisp.cues.cue import Cue, CueAction
from lisp.cues.media_cue import MediaCue
from lisp.layouts.cue_layout import CueLayout
from lisp.layouts.list_layout.control_buttons import ShowControlButtons
from lisp.layouts.list_layout.cue_list_model import CueListModel, \
    RunningCueModel
from lisp.layouts.list_layout.cue_list_view import CueListView
from lisp.layouts.list_layout.info_panel import InfoPanel
from lisp.layouts.list_layout.list_layout_settings import ListLayoutSettings
from lisp.layouts.list_layout.playing_list_widget import RunningCuesListWidget
from lisp.ui.mainwindow import MainWindow
from lisp.ui.settings.app_settings import AppSettings
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.settings.pages.cue_appearance import Appearance
from lisp.ui.settings.pages.cue_general import CueGeneralSettings
from lisp.ui.settings.pages.media_cue_settings import MediaCueSettings
from lisp.ui.ui_utils import translate

AppSettings.register_settings_widget(ListLayoutSettings)


class EndListBehavior(Enum):
    Stop = 'Stop'
    Restart = 'Restart'


class ListLayout(QWidget, CueLayout):
    NAME = 'List Layout'
    DESCRIPTION = QT_TRANSLATE_NOOP('LayoutDescription',
                                    'Organize the cues in a list')
    DETAILS = [
        QT_TRANSLATE_NOOP('LayoutDetails',
                          'SHIFT + Space or Double-Click to edit a cue'),
        QT_TRANSLATE_NOOP('LayoutDetails',
                          'CTRL + Left Click to select cues'),
        QT_TRANSLATE_NOOP('LayoutDetails',
                          'To copy cues drag them while pressing CTRL'),
        QT_TRANSLATE_NOOP('LayoutDetails', 'To move cues drag them')
    ]

    def __init__(self, cue_model, **kwargs):
        super().__init__(cue_model=cue_model, **kwargs)
        self.setLayout(QGridLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._model_adapter = CueListModel(self._cue_model)
        self._model_adapter.item_added.connect(self.__cue_added)
        self._model_adapter.item_removed.connect(self.__cue_removed)

        self._playing_model = RunningCueModel(self._cue_model)
        self._context_item = None
        self._next_cue_index = 0

        self._show_dbmeter = config['ListLayout'].getboolean('ShowDbMeters')
        self._seek_visible = config['ListLayout'].getboolean('ShowSeek')
        self._accurate_time = config['ListLayout'].getboolean('ShowAccurate')
        self._auto_continue = config['ListLayout'].getboolean('AutoContinue')
        self._show_playing = config['ListLayout'].getboolean('ShowPlaying')
        self._go_key = config['ListLayout']['GoKey']
        self._go_key_sequence = QKeySequence(self._go_key,
                                             QKeySequence.NativeText)

        try:
            self._end_list = EndListBehavior(config['ListLayout']['EndList'])
        except ValueError:
            self._end_list = EndListBehavior.Stop

        # Add layout-specific menus
        self.showPlayingAction = QAction(self)
        self.showPlayingAction.setCheckable(True)
        self.showPlayingAction.setChecked(self._show_playing)
        self.showPlayingAction.triggered.connect(self.set_playing_visible)

        self.showDbMeterAction = QAction(self)
        self.showDbMeterAction.setCheckable(True)
        self.showDbMeterAction.setChecked(self._show_dbmeter)
        self.showDbMeterAction.triggered.connect(self.set_dbmeter_visible)

        self.showSeekAction = QAction(self)
        self.showSeekAction.setCheckable(True)
        self.showSeekAction.setChecked(self._seek_visible)
        self.showSeekAction.triggered.connect(self.set_seek_visible)

        self.accurateTimingAction = QAction(self)
        self.accurateTimingAction.setCheckable(True)
        self.accurateTimingAction.setChecked(self._accurate_time)
        self.accurateTimingAction.triggered.connect(self.set_accurate_time)

        self.autoNextAction = QAction(self)
        self.autoNextAction.setCheckable(True)
        self.autoNextAction.setChecked(self._auto_continue)
        self.autoNextAction.triggered.connect(self.set_auto_next)

        MainWindow().menuLayout.addAction(self.showPlayingAction)
        MainWindow().menuLayout.addAction(self.showDbMeterAction)
        MainWindow().menuLayout.addAction(self.showSeekAction)
        MainWindow().menuLayout.addAction(self.accurateTimingAction)
        MainWindow().menuLayout.addAction(self.autoNextAction)

        # GO-BUTTON (top-left)
        self.goButton = QPushButton('GO', self)
        self.goButton.setFocusPolicy(Qt.NoFocus)
        self.goButton.setFixedWidth(120)
        self.goButton.setFixedHeight(100)
        self.goButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.goButton.setStyleSheet('font-size: 48pt;')
        self.goButton.clicked.connect(self.__go_slot)
        self.layout().addWidget(self.goButton, 0, 0)

        # INFO PANEL (top center)
        self.infoPanel = InfoPanel()
        self.infoPanel.setFixedHeight(100)
        self.layout().addWidget(self.infoPanel, 0, 1)

        # CONTROL-BUTTONS (top-right)
        self.controlButtons = ShowControlButtons(parent=self)
        self.controlButtons.setFixedHeight(100)
        self.controlButtons.stopButton.clicked.connect(self.stop_all)
        self.controlButtons.pauseButton.clicked.connect(self.pause_all)
        self.controlButtons.fadeInButton.clicked.connect(self.fadein_all)
        self.controlButtons.fadeOutButton.clicked.connect(self.fadeout_all)
        self.controlButtons.resumeButton.clicked.connect(self.restart_all)
        self.controlButtons.interruptButton.clicked.connect(self.interrupt_all)
        self.layout().addWidget(self.controlButtons, 0, 2)

        # CUE VIEW (center left)
        self.listView = CueListView(self._model_adapter, self)
        self.listView.itemDoubleClicked.connect(self.double_clicked)
        self.listView.currentItemChanged.connect(self.__current_changed)
        self.listView.context_event.connect(self.context_event)
        self.listView.key_event.connect(self.onKeyPressEvent)
        self.listView.select_cue_event.connect(self.select_event)
        self.layout().addWidget(self.listView, 1, 0, 1, 2)

        # PLAYING VIEW (center right)
        self.playView = RunningCuesListWidget(self._playing_model, parent=self)
        self.playView.dbmeter_visible = self._show_dbmeter
        self.playView.accurate_time = self._accurate_time
        self.playView.seek_visible = self._seek_visible
        self.playView.setMinimumWidth(300)
        self.playView.setMaximumWidth(300)
        self.layout().addWidget(self.playView, 1, 2)

        self.set_playing_visible(self._show_playing)

        # TODO: maybe can be moved outside the layout
        # Add cue preferences widgets
        CueSettingsRegistry().add_item(CueGeneralSettings, Cue)
        CueSettingsRegistry().add_item(MediaCueSettings, MediaCue)
        CueSettingsRegistry().add_item(Appearance)

        # Context menu actions
        self.edit_action = QAction(self)
        self.edit_action.triggered.connect(self.edit_context_cue)

        self.remove_action = QAction(self)
        self.remove_action.triggered.connect(self.remove_context_cue)

        self.select_action = QAction(self)
        self.select_action.triggered.connect(self.select_context_cue)

        self.cm_registry.add_item(self.edit_action)
        self.sep1 = self.cm_registry.add_separator()
        self.cm_registry.add_item(self.remove_action)
        self.cm_registry.add_item(self.select_action)

        self.retranslateUi()

    def retranslateUi(self):
        self.showPlayingAction.setText(
            translate('ListLayout', 'Show playing cues'))
        self.showDbMeterAction.setText(
            translate('ListLayout', 'Show dB-meters'))
        self.showSeekAction.setText(translate('ListLayout', 'Show seek-bars'))
        self.accurateTimingAction.setText(
            translate('ListLayout', 'Show accurate time'))
        self.autoNextAction.setText(
            translate('ListLayout', 'Auto-select next cue'))

        self.edit_action.setText(translate('ListLayout', 'Edit cue'))
        self.remove_action.setText(translate('ListLayout', 'Remove'))
        self.select_action.setText(translate('ListLayout', 'Select'))

    @CueLayout.model_adapter.getter
    def model_adapter(self):
        return self._model_adapter

    def current_index(self):
        return self.listView.currentIndex().row()

    def set_current_index(self, index):
        if self._end_list == EndListBehavior.Restart:
            index %= len(self.model_adapter)

        if 0 <= index < self.listView.topLevelItemCount():
            next_item = self.listView.topLevelItem(index)
            self.listView.setCurrentItem(next_item)

    def go(self, action=CueAction.Default, advance=1):
        current_cue = self.current_cue()
        if current_cue is not None:
            current_cue.execute(action)
            self.cue_executed.emit(current_cue)

            if self._auto_continue:
                self.set_current_index(self.current_index() + advance)

    def current_item(self):
        if self._model_adapter:
            return self.listView.currentItem()

    def select_context_cue(self):
        self._context_item.selected = not self._context_item.selected

    def set_accurate_time(self, accurate):
        self._accurate_time = accurate
        self.playView.accurate_time = accurate

    def set_auto_next(self, enable):
        self._auto_continue = enable

    def set_seek_visible(self, visible):
        self._seek_visible = visible
        self.playView.seek_visible = visible

    def set_dbmeter_visible(self, visible):
        self._show_dbmeter = visible
        self.playView.dbmeter_visible = visible

    def set_playing_visible(self, visible):
        self._show_playing = visible
        self.playView.setVisible(visible)
        self.controlButtons.setVisible(visible)

    def onKeyPressEvent(self, e):
        if not e.isAutoRepeat():
            keys = e.key()
            modifiers = e.modifiers()

            if modifiers & Qt.ShiftModifier:
                keys += Qt.SHIFT
            if modifiers & Qt.ControlModifier:
                keys += Qt.CTRL
            if modifiers & Qt.AltModifier:
                keys += Qt.ALT
            if modifiers & Qt.MetaModifier:
                keys += Qt.META

            if QKeySequence(keys) in self._go_key_sequence:
                self.go()
            elif e.key() == Qt.Key_Space:
                if qApp.keyboardModifiers() == Qt.ShiftModifier:
                    cue = self.current_cue()
                    if cue is not None:
                        self.edit_cue(cue)
                elif qApp.keyboardModifiers() == Qt.ControlModifier:
                    item = self.current_item()
                    if item is not None:
                        item.selected = not item.selected
            else:
                self.key_pressed.emit(e)

        e.accept()

    def double_clicked(self, event):
        cue = self.current_cue()
        if cue is not None:
            self.edit_cue(cue)

    def select_event(self, event):
        item = self.listView.itemAt(event.pos())
        if item is not None:
            item.selected = not item.selected

    def context_event(self, event):
        self._context_item = self.listView.itemAt(event.pos())
        if self._context_item is not None:
            self.show_cue_context_menu(event.globalPos())

    def contextMenuEvent(self, event):
        if self.listView.geometry().contains(event.pos()):
            self.show_context_menu(event.globalPos())

    def remove_context_cue(self):
        self._model_adapter.remove(self.get_context_cue())

    def edit_context_cue(self):
        self.edit_cue(self.get_context_cue())

    def stop_all(self):
        fade = config['ListLayout'].getboolean('StopAllFade')
        for cue in self._model_adapter:
            cue.stop(fade=fade)

    def interrupt_all(self):
        fade = config['ListLayout'].getboolean('InterruptAllFade')
        for cue in self._model_adapter:
            cue.interrupt(fade=fade)

    def pause_all(self):
        fade = config['ListLayout'].getboolean('PauseAllFade')
        for cue in self._model_adapter:
            cue.pause(fade=fade)

    def restart_all(self):
        # TODO: change to resume
        fade = config['ListLayout'].getboolean('ResumeAllFade')
        for cue in self._model_adapter:
            cue.restart(fade=fade)

    def fadein_all(self):
        for cue in self._model_adapter:
            cue.execute(CueAction.FadeIn)

    def fadeout_all(self):
        for cue in self._model_adapter:
            cue.execute(CueAction.FadeOut)

    def get_selected_cues(self, cue_class=Cue):
        cues = []
        for index in range(self.listView.topLevelItemCount()):
            item = self.listView.topLevelItem(index)
            if item.selected and isinstance(item.cue, cue_class):
                cues.append(item.cue)
        return cues

    def finalize(self):
        MainWindow().menuLayout.clear()

        # Disconnect menu-actions signals
        self.edit_action.triggered.disconnect()
        self.remove_action.triggered.disconnect()
        self.select_action.triggered.disconnect()

        # Remove context-items
        self.cm_registry.remove_item(self.edit_action)
        self.cm_registry.remove_item(self.sep1)
        self.cm_registry.remove_item(self.remove_action)
        self.cm_registry.remove_item(self.select_action)

        # Delete the layout
        self.deleteLater()

    def get_context_cue(self):
        return self._context_item.cue

    def select_all(self, cue_class=Cue):
        for index in range(self.listView.topLevelItemCount()):
            if isinstance(self.model_adapter.item(index), cue_class):
                self.listView.topLevelItem(index).selected = True

    def deselect_all(self, cue_class=Cue):
        for index in range(self.listView.topLevelItemCount()):
            if isinstance(self.model_adapter.item(index), cue_class):
                self.listView.topLevelItem(index).selected = False

    def invert_selection(self):
        for index in range(self.listView.topLevelItemCount()):
            item = self.listView.topLevelItem(index)
            item.selected = not item.selected

    def __go_slot(self):
        self.go()

    def __current_changed(self, new_item, current_item):
        try:
            index = self.listView.indexOfTopLevelItem(new_item)
            cue = self.model_adapter.item(index)
            self.infoPanel.cue_changed(cue)
        except IndexError:
            self.infoPanel.cue_changed(None)

    def __cue_added(self, cue):
        cue.next.connect(self.__cue_next, Connection.QtQueued)

    def __cue_removed(self, cue):
        if isinstance(cue, MediaCue):
            cue.media.interrupt()
        else:
            cue.stop()

    def __cue_next(self, cue):
        try:
            next_index = cue.index + 1
            if next_index < len(self._model_adapter):
                next_cue = self._model_adapter.item(next_index)
                next_cue.execute()

                if self._auto_continue and next_cue == self.current_cue():
                    self.set_current_index(next_index + 1)
        except(IndexError, KeyError):
            pass
