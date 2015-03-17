##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from itertools import chain

from PyQt5 import QtCore
from PyQt5.QtWidgets import QTabWidget, QAction, QInputDialog, QWidget, \
    QApplication, QMessageBox
from lisp.utils.configuration import config

from lisp.cues.action_cue import ActionCue
from lisp.cues.cue import Cue
from lisp.cues.cue_factory import CueFactory
from lisp.cues.media_cue import MediaCue
from lisp.layouts.cart_layout.cuewidget import CueWidget
from lisp.layouts.cart_layout.gridwidget import GridWidget
from lisp.layouts.cart_layout.mediawidget import MediaCueWidget
from lisp.layouts.cart_layout.preferences import CartLayoutPreferences
from lisp.layouts.cue_layout import CueLayout
from lisp.ui.settings.app_settings import AppSettings
from lisp.ui.settings.sections.cue_appearance import Appearance
from lisp.ui.settings.sections.media_cue_general import MediaCueGeneral


AppSettings.register_settings_widget(CartLayoutPreferences)


class CartLayout(QTabWidget, CueLayout):

    NAME = 'Cart Layout'
    DESCRIPTION = '''
                    This layout organize the cues in multiple grids like a
                     cart player:
                    <ul>
                        <li>Unlimited pages;
                        <li>Cues are displayed as buttons;
                        <li>Cues can be moved in the grid;
                        <li>Cues can be moved from a page to another;
                    </ul> '''

    # I need to redefine those from CueLayout
    key_pressed = CueLayout.key_pressed
    cue_added = CueLayout.cue_added
    cue_removed = CueLayout.cue_removed
    focus_changed = CueLayout.focus_changed

    def __init__(self, app, **kwds):
        super().__init__(**kwds)

        self.menuLayout = app.mainWindow.menuLayout

        self._columns = int(config['CartLayout']['GridColumns'])
        self._rows = int(config['CartLayout']['GridRows'])
        self._page_size = self._columns * self._rows

        self._grids = []
        self._context_widget = None

        self._show_seek = config['CartLayout']['ShowSeek'] == 'True'
        self._show_dbmeter = config['CartLayout']['ShowDbMeters'] == 'True'
        self._accurate_timing = config['CartLayout']['ShowAccurate'] == 'True'
        self._coundown_mode = config['CartLayout']['countDown'] == 'True'
        self._auto_add_page = config['CartLayout']['autoAddPage'] == 'True'

        # Add layout-specific menus
        self.new_page_action = QAction(self)
        self.new_page_action.triggered.connect(self.add_page)

        self.new_pages_action = QAction(self)
        self.new_pages_action.triggered.connect(self.add_pages)

        self.rm_current_page_action = QAction(self)
        self.rm_current_page_action.triggered.connect(self.remove_current_page)

        self.countdown_mode = QAction(self)
        self.countdown_mode.setCheckable(True)
        self.countdown_mode.setChecked(self._coundown_mode)
        self.countdown_mode.triggered.connect(self.set_countdown_mode)

        self.show_sliders_action = QAction(self)
        self.show_sliders_action.setCheckable(True)
        self.show_sliders_action.setChecked(self._show_seek)
        self.show_sliders_action.triggered.connect(self.set_seek_visible)

        self.show_vumeter_action = QAction(self)
        self.show_vumeter_action.setCheckable(True)
        self.show_vumeter_action.setChecked(self._show_dbmeter)
        self.show_vumeter_action.triggered.connect(self.set_dbmeter_visible)

        self.show_accurate_action = QAction(self)
        self.show_accurate_action.setCheckable(True)
        self.show_accurate_action.setChecked(self._accurate_timing)
        self.show_accurate_action.triggered.connect(self.set_accurate)

        self.menuLayout.addAction(self.new_page_action)
        self.menuLayout.addAction(self.new_pages_action)
        self.menuLayout.addAction(self.rm_current_page_action)
        self.menuLayout.addSeparator()
        self.menuLayout.addAction(self.countdown_mode)
        self.menuLayout.addAction(self.show_sliders_action)
        self.menuLayout.addAction(self.show_vumeter_action)
        self.menuLayout.addAction(self.show_accurate_action)

        # Add cue preferences widgets
        self.add_settings_section(MediaCueGeneral, MediaCue)
        self.add_settings_section(Appearance)

        # Context menu actions
        self.edit_action = QAction(self)
        self.edit_action.triggered.connect(self._edit_cue_action)

        self.remove_action = QAction(self)
        self.remove_action.triggered.connect(self._remove_cue_action)

        self.select_action = QAction(self)
        self.select_action.triggered.connect(self.select_context_cue)

        # MediaCue(s) context action
        self.play_action = QAction(self)
        self.play_action.triggered.connect(self.play_context_cue)

        self.pause_action = QAction(self)
        self.pause_action.triggered.connect(self.pause_context_cue)

        self.stop_action = QAction(self)
        self.stop_action.triggered.connect(self.stop_context_cue)

        # Register context items
        self.add_context_item(self.edit_action)
        self.sep1 = self.add_context_separator()
        self.add_context_item(self.remove_action)
        self.add_context_item(self.select_action)
        self.sep2 = self.add_context_separator(MediaCue)
        self.add_context_item(self.play_action, MediaCue)
        self.add_context_item(self.pause_action, MediaCue)
        self.add_context_item(self.stop_action, MediaCue)

        self.setAcceptDrops(True)
        self.retranslateUi()

        self.add_page()

    def retranslateUi(self):
        self.new_page_action.setText("Add page")
        self.new_pages_action.setText("Add pages")
        self.rm_current_page_action.setText('Remove current page')
        self.countdown_mode.setText('Countdown mode')
        self.show_sliders_action.setText('Show seek bars')
        self.show_vumeter_action.setText('Show dB-meters')
        self.show_accurate_action.setText('Accurate time')

        self.edit_action.setText('Edit option')
        self.remove_action.setText('Remove')
        self.select_action.setText('Select')
        self.play_action.setText('Play')
        self.pause_action.setText('Pause')
        self.stop_action.setText('Stop')

    def __add_cue__(self, cue, index=None):
        if self.count() == 0:
            self.add_page()

        if isinstance(cue, MediaCue):
            widget = MediaCueWidget(parent=self)
            widget.set_cue(cue)
            widget.set_accurate_timing(self._accurate_timing)
            widget.show_dbmeters(self._show_dbmeter)
            widget.set_countdown_mode(self._coundown_mode)

            widget.seekSlider.setVisible(self._show_seek)
        elif isinstance(cue, ActionCue):
            widget = CueWidget(parent=self)
            widget.set_cue(cue)
        else:
            raise Exception('Cue type not supported')

        if index is None:
            while self._auto_add_page and self.current_grid().isFull():
                if self.currentIndex() == self.count() - 1:
                    self.add_page()
                self.setCurrentIndex(self.currentIndex() + 1)
            index3d = (self.currentIndex(), -1, -1)
        else:
            index3d = self.to_3d_index(index)
            while index3d[0] > self.count() - 1:
                self.add_page()

        # Add the widget
        index = self._grids[index3d[0]].addItem(widget, index3d[1], index3d[2])
        cue['index'] = self.to_1d_index((index3d[0],) + index)

        # widget.focus_changed.connect(self.focus_changed.emit)
        widget.context_menu_request.connect(self._on_context_menu)
        widget.edit_request.connect(self.edit_cue)

        self.cue_added.emit(cue)

    def add_pages(self):
        pages, ok = QInputDialog.getInt(self, 'Input', 'Number of Pages:',
                                        value=1, min=1, max=10)
        if ok:
            for _ in range(pages):
                self.add_page()

    def add_page(self):
        tab = QWidget(self)
        self.addTab(tab, 'Page ' + str(self.count() + 1))

        grid = GridWidget(tab, self._rows, self._columns)
        self._grids.append(grid)

        grid.move_drop_event.connect(self.move_widget)
        grid.copy_drop_event.connect(self.copy_widget)
        grid.show()

    def clear_layout(self):
        for cue in self.get_cues():
            self.__remove_cue__(cue)

        self._grids = []
        self.clear()

    def copy_widget(self, widget, index):
        index = self.to_1d_index((self.currentIndex(), index[1], index[2]))
        new_cue = CueFactory.clone_cue(widget.cue)

        self.add_cue(new_cue, index)

    def current_grid(self):
        return self._grids[self.currentIndex()]

    def deselect_all(self):
        for widget in chain(*chain(*self._grids)):
            if widget is not None and widget.selected:
                widget.select()

    def destroy_layout(self):
        self.clear_layout()
        self.menuLayout.clear()

        # Remove context-items
        self.remove_context_item(self.edit_action)
        self.remove_context_item(self.sep1)
        self.remove_context_item(self.remove_action)
        self.remove_context_item(self.select_action)
        self.remove_context_item(self.sep2)
        self.remove_context_item(self.play_action)
        self.remove_context_item(self.pause_action)
        self.remove_context_item(self.stop_action)

        # Remove settings-sections
        self.remove_settings_section(Appearance)
        self.remove_settings_section(MediaCueGeneral)

        # !! Delete the layout references !!
        self.deleteLater()

    def dragEnterEvent(self, e):
        if QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
            e.setDropAction(QtCore.Qt.MoveAction)
        elif QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
            e.setDropAction(QtCore.Qt.CopyAction)
        e.accept()

    def dragMoveEvent(self, e):
        if(self.tabBar().contentsRect().contains(e.pos())):
            self.setCurrentIndex(self.tabBar().tabAt(e.pos()))
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        e.ignore()

    def get_context_cue(self):
        if self._context_widget is not None:
            return self._context_widget.cue

    def get_cues(self, cue_class=Cue):
        # w -> widget
        cues = []
        for w in chain(*chain(*self._grids)):
            if w is not None and isinstance(w.cue, cue_class):
                cues.append(w.cue)
        return cues

    def get_cue_at(self, index):
        page, row, col = self.to_3d_index(index)
        widget = self._grids[page].itemAt(row, col)
        if widget is not None:
            return widget.cue

    def get_cue_by_id(self, cue_id):
        for widget in chain(*chain(*self._grids)):
            if widget is not None and widget.cue.cue_id() == cue_id:
                return widget.cue

    def get_selected_cues(self, cue_class=Cue):
        # w -> widget
        cues = []
        for w in chain(*chain(*self._grids)):
            if w is not None and isinstance(w.cue, cue_class) and w.selected:
                cues.append(w.cue)
        return cues

    def invert_selection(self):
        for widget in chain(*chain(*self._grids)):
            if widget is not None:
                widget.select()

    def keyPressEvent(self, event):
        self.key_pressed.emit(event)
        event.ignore()

    def move_widget(self, widget, index):
        widget.cue.widget = widget
        index = (self.currentIndex(), ) + index[1:]
        self.move_cue(widget.cue, self.to_1d_index(index))

    def __move_cue__(self, cue, index):
        current = self.to_3d_index(cue['index'])
        new = self.to_3d_index(index)

        self._grids[current[0]].removeItemAt(current[1], current[2])
        self._grids[new[0]].addItem(cue.widget, new[1], new[2])

        cue['index'] = index
        del cue.widget

    def __remove_cue__(self, cue):
        cue.finalize()

        index = self.to_3d_index(cue['index'])
        self._grids[index[0]].removeItemAt(index[1], index[2])

        self.cue_removed.emit(cue)

    def remove_current_page(self):
        if len(self._grids) > 0:
            reply = QMessageBox.question(self, "Warning",
                                         "Removing the current page every "
                                         "media contained will be lost, "
                                         "are you sure to continue?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.remove_page(self.currentIndex())
        else:
            QMessageBox.critical(None, 'Error Message', 'No pages to remove')

    def remove_page(self, page):
        if len(self._grids) > page >= 0:

            for widget in chain(*self._grids[page]):
                if widget is not None:
                    self.__remove_cue__(widget.cue)

            self.removeTab(page)
            self.tabRemoved(page)
            self._grids.remove(self._grids[page])

            # Rename every successive tab accordingly
            for n in range(page, self.count()):
                self.setTabText(n, 'Page ' + str(n + 1))

                # Update the indexes
                for widget in chain(*self._grids[page]):
                    if widget is not None:
                        widget.cue['index'] -= self._page_size
        else:
            QMessageBox.critical(None, 'Error Message', 'No page ' + str(page))

    def select_all(self):
        for widget in chain(*chain(*self._grids)):
            if widget is not None and not widget.selected:
                    widget.select()

    def select_context_cue(self):
        self._context_widget.select()

    def set_countdown_mode(self, mode):
        self._coundown_mode = mode

        for widget in chain(*chain(*self._grids)):
            if isinstance(widget, MediaCueWidget):
                widget.set_countdown_mode(mode)

    def set_accurate(self, enable):
        self._accurate_timing = enable

        for widget in chain(*chain(*self._grids)):
            if isinstance(widget, MediaCueWidget):
                widget.set_accurate_timing(enable)

    def set_seek_visible(self, visible):
        self._show_seek = visible

        for widget in chain(*chain(*self._grids)):
            if isinstance(widget, MediaCueWidget):
                widget.seekSlider.setVisible(visible)

    def set_dbmeter_visible(self, visible):
        self._show_dbmeter = visible

        for widget in chain(*chain(*self._grids)):
            if isinstance(widget, MediaCueWidget):
                widget.show_dbmeters(visible)

    def to_3d_index(self, index):
        page = index // self._page_size
        row = (index % self._page_size) // self._columns
        column = (index % self._page_size) % self._columns

        return (page, row, column)

    def to_1d_index(self, index):
        if len(index) == 3:
            page = index[0] * self._page_size
            row = index[1] * self._columns
            return page + row + index[2]
        else:
            return -1

    def play_context_cue(self):
        self.get_context_cue().media.play()

    def pause_context_cue(self):
        self.get_context_cue().media.pause()

    def stop_context_cue(self):
        self.get_context_cue().media.stop()

    def _on_context_menu(self, widget, position):
        self._context_widget = widget
        self.show_context_menu(position)

    def _edit_cue_action(self):
        self.edit_cue(self.get_context_cue())

    def _remove_cue_action(self):
        self.remove_cue(self.get_context_cue())
