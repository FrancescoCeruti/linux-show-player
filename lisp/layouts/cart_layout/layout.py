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

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import QTabWidget, QAction, QInputDialog, qApp, \
    QMessageBox

from lisp.core.configuration import config
from lisp.core.signal import Connection
from lisp.cues.cue import Cue
from lisp.cues.cue_factory import CueFactory
from lisp.cues.media_cue import MediaCue
from lisp.layouts.cart_layout.cart_layout_settings import CartLayoutSettings
from lisp.layouts.cart_layout.cue_cart_model import CueCartModel
from lisp.layouts.cart_layout.cue_widget import CueWidget
from lisp.layouts.cart_layout.page_widget import PageWidget
from lisp.layouts.cue_layout import CueLayout
from lisp.ui.mainwindow import MainWindow
from lisp.ui.settings.app_settings import AppSettings
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.settings.pages.cue_appearance import Appearance
from lisp.ui.settings.pages.cue_general import CueGeneralSettings
from lisp.ui.settings.pages.media_cue_settings import MediaCueSettings
from lisp.ui.ui_utils import translate

AppSettings.register_settings_widget(CartLayoutSettings)


class CartLayout(QTabWidget, CueLayout):
    NAME = 'Cart Layout'
    DESCRIPTION = translate('LayoutDescription',
                            'Organize cues in grid like pages')
    DETAILS = [
        QT_TRANSLATE_NOOP('LayoutDetails', 'Click a cue to run it'),
        QT_TRANSLATE_NOOP('LayoutDetails', 'SHIFT + Click to edit a cue'),
        QT_TRANSLATE_NOOP('LayoutDetails', 'CTRL + Click to select a cue'),
        QT_TRANSLATE_NOOP('LayoutDetails',
                          'To copy cues drag them while pressing CTRL'),
        QT_TRANSLATE_NOOP('LayoutDetails',
                          'To copy cues drag them while pressing SHIFT')
    ]

    def __init__(self, cue_model, **kwargs):
        super().__init__(cue_model=cue_model, **kwargs)
        self.tabBar().setObjectName('CartTabBar')

        self.__columns = int(config['CartLayout']['GridColumns'])
        self.__rows = int(config['CartLayout']['GridRows'])
        self.__pages = []
        self.__context_widget = None

        self._show_seek = config['CartLayout'].getboolean('ShowSeek')
        self._show_dbmeter = config['CartLayout'].getboolean('ShowDbMeters')
        self._show_volume = config['CartLayout'].getboolean('ShowVolume')
        self._accurate_timing = config['CartLayout'].getboolean('ShowAccurate')
        self._countdown_mode = config['CartLayout'].getboolean('CountDown')
        self._auto_add_page = config['CartLayout'].getboolean('AutoAddPage')

        self._model_adapter = CueCartModel(cue_model, self.__rows, self.__columns)
        self._model_adapter.item_added.connect(self.__cue_added, Connection.QtQueued)
        self._model_adapter.item_removed.connect(self.__cue_removed, Connection.QtQueued)
        self._model_adapter.item_moved.connect(self.__cue_moved, Connection.QtQueued)
        self._model_adapter.model_reset.connect(self.__model_reset)

        # Add layout-specific menus
        self.new_page_action = QAction(self)
        self.new_page_action.triggered.connect(self.add_page)
        self.new_pages_action = QAction(self)
        self.new_pages_action.triggered.connect(self.add_pages)
        self.rm_current_page_action = QAction(self)
        self.rm_current_page_action.triggered.connect(self.remove_current_page)

        self.countdown_mode = QAction(self)
        self.countdown_mode.setCheckable(True)
        self.countdown_mode.setChecked(self._countdown_mode)
        self.countdown_mode.triggered.connect(self.set_countdown_mode)

        self.show_seek_action = QAction(self)
        self.show_seek_action.setCheckable(True)
        self.show_seek_action.setChecked(self._show_seek)
        self.show_seek_action.triggered.connect(self.set_seek_visible)

        self.show_dbmeter_action = QAction(self)
        self.show_dbmeter_action.setCheckable(True)
        self.show_dbmeter_action.setChecked(self._show_dbmeter)
        self.show_dbmeter_action.triggered.connect(self.set_dbmeter_visible)

        self.show_volume_action = QAction(self)
        self.show_volume_action.setCheckable(True)
        self.show_volume_action.setChecked(self._show_volume)
        self.show_volume_action.triggered.connect(self.set_volume_visible)

        self.show_accurate_action = QAction(self)
        self.show_accurate_action.setCheckable(True)
        self.show_accurate_action.setChecked(self._accurate_timing)
        self.show_accurate_action.triggered.connect(self.set_accurate)

        layoutMenu = MainWindow().menuLayout
        layoutMenu.addAction(self.new_page_action)
        layoutMenu.addAction(self.new_pages_action)
        layoutMenu.addAction(self.rm_current_page_action)
        layoutMenu.addSeparator()
        layoutMenu.addAction(self.countdown_mode)
        layoutMenu.addAction(self.show_seek_action)
        layoutMenu.addAction(self.show_dbmeter_action)
        layoutMenu.addAction(self.show_volume_action)
        layoutMenu.addAction(self.show_accurate_action)

        # TODO: maybe can be moved outside the layout
        # Add cue preferences widgets
        CueSettingsRegistry().add_item(CueGeneralSettings, Cue)
        CueSettingsRegistry().add_item(MediaCueSettings, MediaCue)
        CueSettingsRegistry().add_item(Appearance)

        # Cue(s) context-menu actions
        self.edit_action = QAction(self)
        self.edit_action.triggered.connect(self._edit_cue_action)
        self.cm_registry.add_item(self.edit_action)

        self.sep1 = self.cm_registry.add_separator()

        self.remove_action = QAction(self)
        self.remove_action.triggered.connect(self._remove_cue_action)
        self.cm_registry.add_item(self.remove_action)

        self.select_action = QAction(self)
        self.select_action.triggered.connect(self.select_context_cue)
        self.cm_registry.add_item(self.select_action)

        self.sep2 = self.cm_registry.add_separator(MediaCue)

        # MediaCue(s) context-menu actions
        self.play_action = QAction(self)
        self.play_action.triggered.connect(self._play_context_cue)
        self.cm_registry.add_item(self.play_action, MediaCue)

        self.pause_action = QAction(self)
        self.pause_action.triggered.connect(self._pause_context_cue)
        self.cm_registry.add_item(self.pause_action, MediaCue)

        self.stop_action = QAction(self)
        self.stop_action.triggered.connect(self._stop_context_cue)
        self.cm_registry.add_item(self.stop_action, MediaCue)

        self.reset_volume_action = QAction(self)
        self.reset_volume_action.triggered.connect(self._reset_cue_volume)
        self.cm_registry.add_item(self.reset_volume_action, MediaCue)

        self.setAcceptDrops(True)
        self.retranslateUi()

        self.add_page()

    def retranslateUi(self):
        self.new_page_action.setText(translate('CartLayout', 'Add page'))
        self.new_pages_action.setText(translate('CartLayout', 'Add pages'))
        self.rm_current_page_action.setText(
            translate('CartLayout', 'Remove current page'))
        self.countdown_mode.setText(translate('CartLayout', 'Countdown mode'))
        self.show_seek_action.setText(translate('CartLayout', 'Show seek-bars'))
        self.show_dbmeter_action.setText(
            translate('CartLayout', 'Show dB-meters'))
        self.show_volume_action.setText(translate('CartLayout', 'Show volume'))
        self.show_accurate_action.setText(
            translate('CartLayout', 'Show accurate time'))

        self.edit_action.setText(translate('CartLayout', 'Edit cue'))
        self.remove_action.setText(translate('CartLayout', 'Remove'))
        self.select_action.setText(translate('CartLayout', 'Select'))
        self.play_action.setText(translate('CartLayout', 'Play'))
        self.pause_action.setText(translate('CartLayout', 'Pause'))
        self.stop_action.setText(translate('CartLayout', 'Stop'))
        self.reset_volume_action.setText(translate('CartLayout', 'Reset volume'))

    @CueLayout.model_adapter.getter
    def model_adapter(self):
        return self._model_adapter

    def add_pages(self):
        pages, accepted = QInputDialog.getInt(
            self,
            translate('CartLayout', 'Add pages'),
            translate('CartLayout', 'Number of Pages:'),
            value=1, min=1, max=10)

        if accepted:
            for _ in range(pages):
                self.add_page()

    def add_page(self):
        page = PageWidget(self.__rows, self.__columns, self)
        page.move_drop_event.connect(self._move_widget)
        page.copy_drop_event.connect(self._copy_widget)

        self.addTab(page, 'Page ' + str(self.count() + 1))
        self.__pages.append(page)

    def select_context_cue(self):
        self.__context_widget.selected = not self.__context_widget.selected

    def select_all(self, cue_class=Cue):
        for widget in self.widgets():
            if isinstance(widget.cue, cue_class):
                widget.selected = True

    def deselect_all(self, cue_class=Cue):
        for widget in self.widgets():
            if isinstance(widget.cue, cue_class):
                widget.selected = False

    def invert_selection(self):
        for widget in self.widgets():
            widget.selected = not widget.selected

    def contextMenuEvent(self, event):
        # For some reason the currentWidget geometry does not include the
        # vertical offset created by the tabBar.
        geometry = self.currentWidget().geometry().translated(0, self.tabBar().geometry().height())
        if geometry.contains(event.pos()):
            self.show_context_menu(event.globalPos())

    def dragEnterEvent(self, event):
        if qApp.keyboardModifiers() == Qt.ControlModifier:
            event.setDropAction(Qt.MoveAction)
            event.accept()
        elif qApp.keyboardModifiers() == Qt.ShiftModifier:
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if self.tabBar().contentsRect().contains(event.pos()):
            self.setCurrentIndex(self.tabBar().tabAt(event.pos()))
            event.accept()

    def dropEvent(self, e):
        e.ignore()

    def keyPressEvent(self, event):
        self.key_pressed.emit(event)
        event.ignore()

    def get_context_cue(self):
        if self.__context_widget is not None:
            return self.__context_widget.cue

    def get_selected_cues(self, cue_class=Cue):
        # w -> widget
        cues = []
        for widget in self.widgets():
            if widget.selected:
                cues.append(widget.cue)
        return cues

    def remove_current_page(self):
        if self.__pages:
            confirm = QMessageBox()
            confirm.setIcon(confirm.Question)
            confirm.setWindowTitle(translate('CartLayout', 'Warning'))
            confirm.setText(
                translate('CartLayout', 'Every cue in the page will be lost.'))
            confirm.setInformativeText(
                translate('CartLayout', 'Are you sure to continue?'))
            confirm.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            confirm.setDefaultButton(QMessageBox.No)

            if confirm.exec_() == QMessageBox.Yes:
                self.remove_page(self.currentIndex())

    def remove_page(self, page):
        if len(self.__pages) > page >= 0:
            self._model_adapter.remove_page(page)

            self.removeTab(page)
            self.tabRemoved(page)
            page_widget = self.__pages.pop(page)
            page_widget.move_drop_event.disconnect()
            page_widget.copy_drop_event.disconnect()

            # Rename every successive tab accordingly
            text = translate('CartLayout', 'Page') + ' {}'
            for n in range(page, self.count()):
                self.setTabText(n, text.format(n + 1))

    def widgets(self):
        for page in self.__pages:
            for widget in page.widgets():
                yield widget

    def set_countdown_mode(self, mode):
        self._countdown_mode = mode
        for widget in self.widgets():
            widget.set_countdown_mode(mode)

    def set_accurate(self, enable):
        self._accurate_timing = enable
        for widget in self.widgets():
            widget.set_accurate_timing(enable)

    def set_seek_visible(self, visible):
        self._show_seek = visible
        for widget in self.widgets():
            widget.show_seek_slider(visible)

    def set_dbmeter_visible(self, visible):
        self._show_dbmeter = visible
        for widget in self.widgets():
            widget.show_dbmeters(visible)

    def set_volume_visible(self, visible):
        self._show_volume = visible
        for widget in self.widgets():
            widget.show_volume_slider(visible)

    def to_3d_index(self, index):
        page_size = self.__rows * self.__columns

        page = index // page_size
        row = (index % page_size) // self.__columns
        column = (index % page_size) % self.__columns

        return page, row, column

    def to_1d_index(self, index):
        try:
            page, row, column = index
            page *= self.__rows * self.__columns
            row *= self.__columns
            return page + row + column
        except(TypeError, ValueError):
            return -1

    def finalize(self):
        MainWindow().menuLayout.clear()

        # Disconnect menu-actions signals
        self.edit_action.triggered.disconnect()
        self.remove_action.triggered.disconnect()
        self.select_action.triggered.disconnect()
        self.play_action.triggered.disconnect()
        self.pause_action.triggered.disconnect()
        self.stop_action.triggered.disconnect()
        self.reset_volume_action.disconnect()

        # Remove context-items
        self.cm_registry.remove_item(self.edit_action)
        self.cm_registry.remove_item(self.sep1)
        self.cm_registry.remove_item(self.remove_action)
        self.cm_registry.remove_item(self.select_action)
        self.cm_registry.remove_item(self.sep2)
        self.cm_registry.remove_item(self.play_action)
        self.cm_registry.remove_item(self.pause_action)
        self.cm_registry.remove_item(self.stop_action)
        self.cm_registry.remove_item(self.reset_volume_action)

        # Delete the layout
        self.deleteLater()

    def _move_widget(self, widget, to_row, to_column):
        new_index = self.to_1d_index((self.currentIndex(), to_row, to_column))
        self._model_adapter.move(widget.cue.index, new_index)

    def _copy_widget(self, widget, to_row, to_column):
        new_index = self.to_1d_index((self.currentIndex(), to_row, to_column))
        new_cue = CueFactory.clone_cue(widget.cue)

        self._model_adapter.insert(new_cue, new_index)

    def _play_context_cue(self):
        self.get_context_cue().media.play()

    def _pause_context_cue(self):
        self.get_context_cue().media.pause()

    def _stop_context_cue(self):
        self.get_context_cue().media.stop()

    def _on_context_menu(self, widget, position):
        self.__context_widget = widget
        self.show_cue_context_menu(position)

    def _edit_cue_action(self):
        self.edit_cue(self.get_context_cue())

    def _remove_cue_action(self):
        self._model_adapter.remove(self.get_context_cue())
        self.__context_widget = None

    def _reset_cue_volume(self):
        self.__context_widget.reset_volume()

    def __cue_added(self, cue):
        page, row, column = self.to_3d_index(cue.index)

        widget = CueWidget(cue)
        widget.cue_executed.connect(self.cue_executed.emit)
        widget.context_menu_request.connect(self._on_context_menu)
        widget.edit_request.connect(self.edit_cue)
        widget.set_accurate_timing(self._accurate_timing)
        widget.set_countdown_mode(self._countdown_mode)
        widget.show_dbmeters(self._show_dbmeter)
        widget.show_seek_slider(self._show_seek)
        widget.show_volume_slider(self._show_volume)

        if page >= len(self.__pages):
            self.add_page()

        self.__pages[page].add_widget(widget, row, column)
        self.setCurrentIndex(page)

    def __cue_removed(self, cue):
        if isinstance(cue, MediaCue):
            cue.media.interrupt()
        else:
            cue.stop()

        page, row, column = self.to_3d_index(cue.index)
        widget = self.__pages[page].take_widget(row, column)

        widget.cue_executed.disconnect()
        widget.context_menu_request.disconnect()
        widget.edit_request.disconnect()

        widget.deleteLater()

    def __cue_moved(self, old_index, new_index):
        o_page, o_row, o_column = self.to_3d_index(old_index)
        n_page, n_row, n_column = self.to_3d_index(new_index)

        if o_page == n_page:
            self.__pages[n_page].move_widget(o_row, o_column, n_row, n_column)
        else:
            widget = self.__pages[o_page].take_widget(o_row, o_column)
            self.__pages[n_page].add_widget(widget, n_row, n_column)

    def __model_reset(self):
        self.__context_widget = None
        for page in self.__pages:
            page.reset()
