##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

import weakref

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QAction, QToolBar, QHBoxLayout, QHeaderView, \
    QVBoxLayout, QLabel, QListWidget, QAbstractItemView, QListWidgetItem, qApp
from lisp.core.media import Media
from lisp.utils.configuration import config

from lisp.cues.action_cue import ActionCue
from lisp.cues.cue import Cue
from lisp.cues.cue_factory import CueFactory
from lisp.cues.media_cue import MediaCue
from lisp.layouts.cue_layout import CueLayout
from lisp.layouts.list_layout.actionitem import ActionItem
from lisp.layouts.list_layout.listwidget import ListWidget
from lisp.layouts.list_layout.mediaitem import MediaItem
from lisp.layouts.list_layout.mediawidget_play import PlayingMediaWidget
from lisp.layouts.list_layout.preferences import ListLayoutPreferences
from lisp.ui.settings.app_settings import AppSettings
from lisp.ui.settings.sections.cue_appearance import Appearance
from lisp.ui.settings.sections.media_cue_general import MediaCueGeneral


AppSettings.register_settings_widget(ListLayoutPreferences)


class ListLayout(QWidget, CueLayout):

    NAME = 'List Layout'
    DESCRIPTION = '''
                    This layout organize the cues in a list:
                    <ul>
                        <li>Unlimited cues;
                        <li>Side panel with playing media-cues;
                        <li>Cues can be moved in the list;
                        <li>Keyboard control;
                    </ul>'''

    HEADER = ['', 'Cue', 'Duration', 'Progress']

    # I need to redefine those from CueLayout
    key_pressed = CueLayout.key_pressed
    cue_added = CueLayout.cue_added
    cue_removed = CueLayout.cue_removed
    focus_changed = CueLayout.focus_changed

    def __init__(self, app, **kwds):
        super().__init__(**kwds)

        self.mainWindow = app.mainWindow
        self.menuLayout = self.mainWindow.menuLayout

        self._cue_items = []
        self._playing_widgets = {}
        self._context_item = None

        self._show_dbmeter = config['ListLayout']['ShowDbMeters'] == 'True'
        self._show_seek = config['ListLayout']['ShowSeek'] == 'True'
        self._accurate_time = config['ListLayout']['ShowAccurate'] == 'True'
        self._auto_next = config['ListLayout']['AutoNext'] == 'True'

        # Add layout-specific menus
        self.showDbMeterAction = QAction(self)
        self.showDbMeterAction.setCheckable(True)
        self.showDbMeterAction.setChecked(self._show_dbmeter)
        self.showDbMeterAction.triggered.connect(self.set_dbmeter_visible)

        self.showSeekAction = QAction(self)
        self.showSeekAction.setCheckable(True)
        self.showSeekAction.setChecked(self._show_seek)
        self.showSeekAction.triggered.connect(self.set_seek_visible)

        self.accurateTimingAction = QAction(self)
        self.accurateTimingAction.setCheckable(True)
        self.accurateTimingAction.setChecked(self._accurate_time)
        self.accurateTimingAction.triggered.connect(self.set_accurate_time)

        self.autoNextAction = QAction(self)
        self.autoNextAction.setCheckable(True)
        self.autoNextAction.setChecked(self._auto_next)
        self.autoNextAction.triggered.connect(self.set_auto_next)

        self.menuLayout.addAction(self.showDbMeterAction)
        self.menuLayout.addAction(self.showSeekAction)
        self.menuLayout.addAction(self.accurateTimingAction)
        self.menuLayout.addAction(self.autoNextAction)

        # Add a toolbar to MainWindow
        self.toolBar = QToolBar(self.mainWindow)
        self.toolBar.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)

        self.playAction = QAction(self)
        self.playAction.setIcon(QIcon.fromTheme("media-playback-start"))
        self.playAction.triggered.connect(self.play_current)

        self.pauseAction = QAction(self)
        self.pauseAction.setIcon(QIcon.fromTheme("media-playback-pause"))
        self.pauseAction.triggered.connect(self.pause_current)

        self.stopAction = QAction(self)
        self.stopAction.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.stopAction.triggered.connect(self.stop_current)

        self.stopAllAction = QAction(self)
        self.stopAllAction.font().setBold(True)
        self.stopAllAction.triggered.connect(self.stop_all)

        self.pauseAllAction = QAction(self)
        self.pauseAllAction.font().setBold(True)
        self.pauseAllAction.triggered.connect(self.pause_all)

        self.restartAllAction = QAction(self)
        self.restartAllAction.font().setBold(True)
        self.restartAllAction.triggered.connect(self.restart_all)

        self.toolBar.addAction(self.playAction)
        self.toolBar.addAction(self.pauseAction)
        self.toolBar.addAction(self.stopAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.stopAllAction)
        self.toolBar.addAction(self.pauseAllAction)
        self.toolBar.addAction(self.restartAllAction)

        self.mainWindow.addToolBar(self.toolBar)

        self.hLayout = QHBoxLayout(self)
        self.hLayout.setContentsMargins(5, 5, 5, 5)

        # On the left (cue list)
        self.listView = ListWidget(self)
        self.listView.context_event.connect(self.context_event)
        self.listView.key_event.connect(self.onKeyPressEvent)
        self.listView.drop_move_event.connect(self.move_cue_at)
        self.listView.drop_copy_event.connect(self._copy_cue_at)
        self.listView.setHeaderLabels(self.HEADER)
        self.listView.header().setSectionResizeMode(QHeaderView.Fixed)
        self.listView.header().setSectionResizeMode(self.HEADER.index('Cue'),
                                                    QHeaderView.Stretch)
        self.listView.setColumnWidth(0, 40)
        self.hLayout.addWidget(self.listView)

        self.vLayout = QVBoxLayout()
        self.vLayout.setContentsMargins(0, 0, 0, 0)
        self.vLayout.setSpacing(2)

        # On the right (playing media-cues)
        self.label = QLabel('Playing', self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet('font-size: 17pt; font-weight: bold;')
        self.vLayout.addWidget(self.label)

        self.playView = QListWidget(self)
        self.playView.setMinimumWidth(300)
        self.playView.setMaximumWidth(300)
        self.playView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.playView.setFocusPolicy(QtCore.Qt.NoFocus)
        self.playView.setSelectionMode(QAbstractItemView.NoSelection)
        self.vLayout.addWidget(self.playView)

        self.hLayout.addLayout(self.vLayout)

        # Add cue preferences widgets
        self.add_settings_section(MediaCueGeneral, MediaCue)
        self.add_settings_section(Appearance)

        # Context menu actions
        self.edit_action = QAction(self)
        self.edit_action.triggered.connect(self.edit_context_cue)

        self.remove_action = QAction(self)
        self.remove_action.triggered.connect(self.remove_context_cue)

        self.select_action = QAction(self)
        self.select_action.triggered.connect(self.select_context_cue)

        self.add_context_item(self.edit_action)
        self.sep1 = self.add_context_separator()
        self.add_context_item(self.remove_action)
        self.add_context_item(self.select_action)

        self.retranslateUi()

    def retranslateUi(self):
        self.showDbMeterAction.setText("Show Db-meters")
        self.showSeekAction.setText("Show seek bars")
        self.accurateTimingAction.setText('Accurate timing')
        self.autoNextAction.setText('Auto select next cue')
        self.playAction.setText("Go")
        self.pauseAction.setText("Pause")
        self.stopAction.setText("Stop")
        self.stopAllAction.setText("Stop All")
        self.pauseAllAction.setText("Pause All")
        self.restartAllAction.setText("Restart All")

        self.edit_action.setText('Edit option')
        self.remove_action.setText('Remove')
        self.select_action.setText('Select')

    def current_cue(self):
        item = self.current_item()
        if item is not None:
            return item.cue

    def current_item(self):
        if len(self._cue_items) > 0:
            return self._cue_items[self.listView.currentIndex().row()]

    def select_context_cue(self):
        self._context_item.select()

    def __add_cue__(self, cue, index):
        if isinstance(cue, MediaCue):
            item = MediaItem(cue, self.listView)

            # Use weak-references for avoid cyclic-references with lambda(s)
            wself = weakref.ref(self)
            wcue = weakref.ref(cue)

            cue.media.on_play.connect(lambda: wself().show_playing(wcue()))
            cue.media.interrupted.connect(lambda: wself().hide_playing(wcue()))
            cue.media.stopped.connect(lambda: wself().hide_playing(wcue()))
            cue.media.error.connect(lambda: wself().hide_playing(wcue()))
            cue.media.eos.connect(lambda: wself().hide_playing(wcue()))
        elif isinstance(cue, ActionCue):
            item = ActionItem(cue)
            item.cue = cue
        else:
            raise Exception('Cue type not supported')

        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsDropEnabled)

        if index is None or (index < 0 or index >= len(self._cue_items)):
            cue['index'] = len(self._cue_items)
            self.listView.addTopLevelItem(item)
            self._cue_items.append(item)
        else:
            self.listView.insertTopLevelItem(index, item)
            self._cue_items.insert(index, item)
            for n in range(index, len(self._cue_items)):
                self._cue_items[n].cue['index'] = n

        if isinstance(item, MediaItem):
            item.init()

        if len(self._cue_items) == 1:
            self.listView.setCurrentItem(item)
            self.listView.setFocus()
            self.listView.resizeColumnToContents(1)

        self.cue_added.emit(cue)

    def set_accurate_time(self, enable):
        self._accurate_time = enable

        for i in range(self.playView.count()):
            widget = self.playView.itemWidget(self.playView.item(i))
            widget.set_accurate_time(enable)

        for item in self._cue_items:
            if isinstance(item, MediaItem):
                item.set_accurate_time(enable)

    def set_auto_next(self, enable):
        self._auto_next = enable

    def set_seek_visible(self, visible):
        self._show_seek = visible
        for i in range(self.playView.count()):
            widget = self.playView.itemWidget(self.playView.item(i))
            widget.set_seek_visible(visible)

    def set_dbmeter_visible(self, visible):
        self._show_dbmeter = visible
        for i in range(self.playView.count()):
            widget = self.playView.itemWidget(self.playView.item(i))
            widget.set_dbmeter_visible(visible)

    def show_playing(self, cue):
        if cue not in self._playing_widgets:
            media_time = self._cue_items[cue['index']].media_time
            widget = PlayingMediaWidget(cue, media_time, self.playView)
            widget.set_dbmeter_visible(self._show_dbmeter)
            widget.set_seek_visible(self._show_seek)
            widget.set_accurate_time(self._accurate_time)

            list_item = QListWidgetItem()
            list_item.setSizeHint(widget.size())

            self.playView.addItem(list_item)
            self.playView.setItemWidget(list_item, widget)
            self._playing_widgets[cue] = list_item

    def hide_playing(self, cue):
        if cue in self._playing_widgets:
            list_item = self._playing_widgets.pop(cue)
            widget = self.playView.itemWidget(list_item)
            row = self.playView.indexFromItem(list_item).row()

            self.playView.removeItemWidget(list_item)
            self.playView.takeItem(row)

            widget.destroy_widget()

    def onKeyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Space:
            if qApp.keyboardModifiers() == Qt.ShiftModifier:
                cue = self.current_cue()
                if cue is not None:
                    self.edit_cue(cue)
            elif qApp.keyboardModifiers() == Qt.ControlModifier:
                item = self.current_item()
                if item is not None:
                    item.select()
            else:
                cue = self.current_cue()
                if cue is not None:
                    cue.execute()
                if self._auto_next:
                    nextitem = self.listView.currentIndex().row() + 1
                    if nextitem < self.listView.topLevelItemCount():
                        nextitem = self.listView.topLevelItem(nextitem)
                        self.listView.setCurrentItem(nextitem)
        else:
            self.key_pressed.emit(e)

        e.accept()

    def play_current(self):
        cue = self.current_cue()
        if isinstance(cue, MediaCue):
            cue.media.play()
        else:
            cue.execute()

    def pause_current(self):
        cue = self.current_cue()
        if isinstance(cue, MediaCue):
            cue.media.pause()

    def stop_current(self):
        cue = self.current_cue()
        if isinstance(cue, MediaCue):
            cue.media.stop()

    def context_event(self, event):
        item = self.listView.itemAt(event.pos())
        if item is not None:
            index = self.listView.indexOfTopLevelItem(item)
            self._context_item = self._cue_items[index]
            self.show_context_menu(event.globalPos())
        event.accept()

    def remove_context_cue(self):
        self.remove_cue(self.get_context_cue())

    def edit_context_cue(self):
        self.edit_cue(self.get_context_cue())

    def stop_all(self):
        for item in self._cue_items:
            if isinstance(item.cue, MediaCue):
                item.cue.media.stop()

    def pause_all(self):
        for item in self._cue_items:
            if isinstance(item.cue, MediaCue):
                item.cue.media.pause()

    def restart_all(self):
        for item in self._cue_items:
            if isinstance(item.cue, MediaCue):
                if item.cue.media.state == Media.PAUSED:
                    item.cue.media.play()

    def __remove_cue__(self, cue):
        index = cue['index']
        self.listView.takeTopLevelItem(index)
        self._cue_items.pop(index)

        if isinstance(cue, MediaCue):
            cue.media.interrupt()
            if cue in self._playing_widgets:
                self.hide_playing(self._playing_widgets[cue])

        for item in self._cue_items[index:]:
            item.cue['index'] = item.cue['index'] - 1

        cue.finalize()

        self.cue_removed.emit(cue)

    def move_cue_at(self, old_index, index):
        self.move_cue(self._cue_items[old_index].cue, index)

    def _copy_cue_at(self, old_index, index):
        newcue = CueFactory.clone_cue(self._cue_items[old_index].cue)
        self.add_cue(newcue, index)

    def __move_cue__(self, cue, index):
        item = self._cue_items.pop(cue['index'])
        self._cue_items.insert(index, item)
        self.listView.setCurrentItem(item)

        if isinstance(item, MediaItem):
            item.init()

        for n, item in enumerate(self._cue_items):
            item.cue['index'] = n

    def get_cues(self, cue_class=Cue):
        # i -> item
        return [i.cue for i in self._cue_items if isinstance(i.cue, cue_class)]

    def get_cue_at(self, index):
        if index < len(self._cue_items):
            return self._cue_items[index].cue

    def get_cue_by_id(self, cue_id):
        for item in self._cue_items:
            if item.cue.cue_id() == cue_id:
                return item.cue

    def get_selected_cues(self, cue_class=Cue):
        cues = []
        for item in self._cue_items:
            if item.selected and isinstance(item.cue, cue_class):
                cues.append(item.cue)
        return cues

    def clear_layout(self):
        while len(self._cue_items) > 0:
            self.__remove_cue__(self._cue_items[-1].cue)

    def destroy_layout(self):
        self.clear_layout()
        self.menuLayout.clear()
        self.mainWindow.removeToolBar(self.toolBar)
        self.toolBar.deleteLater()

        # Remove context-items
        self.remove_context_item(self.edit_action)
        self.remove_context_item(self.sep1)
        self.remove_context_item(self.remove_action)
        self.remove_context_item(self.select_action)

        # Remove settings-sections
        self.remove_settings_section(Appearance)
        self.remove_settings_section(MediaCueGeneral)

        # !! Delete the layout references !!
        self.deleteLater()

    def get_context_cue(self):
        return self._context_item.cue

    def select_all(self):
        for item in self._cue_items:
            if not item.selected:
                item.select()

    def deselect_all(self):
        for item in self._cue_items:
            if item.selected:
                item.select()

    def invert_selection(self):
        for item in self._cue_items:
            item.select()
