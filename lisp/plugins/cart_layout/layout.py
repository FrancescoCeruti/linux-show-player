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

from PyQt5.QtCore import QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import QAction, QInputDialog, QMessageBox

from lisp.core.configuration import DummyConfiguration
from lisp.core.properties import ProxyProperty
from lisp.core.signal import Connection
from lisp.cues.cue import Cue
from lisp.cues.cue_factory import CueFactory
from lisp.cues.cue_memento_model import CueMementoAdapter
from lisp.cues.media_cue import MediaCue
from lisp.layout.cue_layout import CueLayout
from lisp.layout.cue_menu import (
    SimpleMenuAction,
    MENU_PRIORITY_CUE,
    MenuActionsGroup,
    MENU_PRIORITY_LAYOUT,
)
from lisp.plugins.cart_layout.cue_widget import CueWidget
from lisp.plugins.cart_layout.model import CueCartModel
from lisp.plugins.cart_layout.page_widget import CartPageWidget
from lisp.plugins.cart_layout.tab_widget import CartTabWidget
from lisp.ui.ui_utils import translate


class CartLayout(CueLayout):
    NAME = QT_TRANSLATE_NOOP("LayoutName", "Cart Layout")
    DESCRIPTION = translate(
        "LayoutDescription", "Organize cues in grid like pages"
    )
    DETAILS = [
        QT_TRANSLATE_NOOP("LayoutDetails", "Click a cue to run it"),
        QT_TRANSLATE_NOOP("LayoutDetails", "SHIFT + Click to edit a cue"),
        QT_TRANSLATE_NOOP("LayoutDetails", "CTRL + Click to select a cue"),
        QT_TRANSLATE_NOOP(
            "LayoutDetails", "To copy cues drag them while pressing CTRL"
        ),
        QT_TRANSLATE_NOOP(
            "LayoutDetails", "To move cues drag them while pressing SHIFT"
        ),
    ]

    Config = DummyConfiguration()

    tabs = ProxyProperty()
    seek_sliders_visible = ProxyProperty()
    volume_control_visible = ProxyProperty()
    dbmeters_visible = ProxyProperty()
    accurate_time = ProxyProperty()
    countdown_mode = ProxyProperty()

    def __init__(self, application):
        super().__init__(application)

        self.__columns = CartLayout.Config["grid.columns"]
        self.__rows = CartLayout.Config["grid.rows"]

        self._cart_model = CueCartModel(
            self.cue_model, self.__rows, self.__columns
        )
        # TODO: move this logic in CartTabWidget ?
        self._cart_model.item_added.connect(self.__cue_added)
        self._cart_model.item_removed.connect(self.__cue_removed)
        self._cart_model.item_moved.connect(self.__cue_moved)
        self._cart_model.model_reset.connect(self.__model_reset)
        self._memento_model = CueMementoAdapter(self._cart_model)

        self._cart_view = CartTabWidget()
        self._cart_view.keyPressed.connect(self._key_pressed)
        self._cart_view.currentChanged.connect(self._tab_changed)

        # Layout menu
        layout_menu = self.app.window.menuLayout

        self.new_page_action = QAction(parent=layout_menu)
        self.new_page_action.triggered.connect(self.add_page)
        layout_menu.addAction(self.new_page_action)

        self.new_pages_action = QAction(parent=layout_menu)
        self.new_pages_action.triggered.connect(self.add_pages)
        layout_menu.addAction(self.new_pages_action)

        self.rm_current_page_action = QAction(parent=layout_menu)
        self.rm_current_page_action.triggered.connect(self.remove_current_page)
        layout_menu.addAction(self.rm_current_page_action)

        layout_menu.addSeparator()

        self.countdown_mode_action = QAction(parent=layout_menu)
        self.countdown_mode_action.setCheckable(True)
        self.countdown_mode_action.triggered.connect(self._set_countdown_mode)
        layout_menu.addAction(self.countdown_mode_action)

        self.show_seek_action = QAction(parent=layout_menu)
        self.show_seek_action.setCheckable(True)
        self.show_seek_action.triggered.connect(self._set_seek_bars_visible)
        layout_menu.addAction(self.show_seek_action)

        self.show_dbmeter_action = QAction(parent=layout_menu)
        self.show_dbmeter_action.setCheckable(True)
        self.show_dbmeter_action.triggered.connect(self._set_dbmeters_visible)
        layout_menu.addAction(self.show_dbmeter_action)

        self.show_volume_action = QAction(parent=layout_menu)
        self.show_volume_action.setCheckable(True)
        self.show_volume_action.triggered.connect(
            self._set_volume_controls_visible
        )
        layout_menu.addAction(self.show_volume_action)

        self.show_accurate_action = QAction(parent=layout_menu)
        self.show_accurate_action.setCheckable(True)
        self.show_accurate_action.triggered.connect(self._set_accurate_time)
        layout_menu.addAction(self.show_accurate_action)

        self._set_countdown_mode(CartLayout.Config["countdownMode"])
        self._set_dbmeters_visible(CartLayout.Config["show.dBMeters"])
        self._set_accurate_time(CartLayout.Config["show.accurateTime"])
        self._set_seek_bars_visible(CartLayout.Config["show.seekSliders"])
        self._set_volume_controls_visible(
            CartLayout.Config["show.volumeControls"]
        )

        # Context menu actions
        self._edit_actions_group = MenuActionsGroup(priority=MENU_PRIORITY_CUE)
        self._edit_actions_group.add(
            SimpleMenuAction(
                translate("ListLayout", "Edit cue"),
                self.edit_cue,
                translate("ListLayout", "Edit selected cues"),
                self.edit_cues,
            ),
            SimpleMenuAction(
                translate("ListLayout", "Remove cue"),
                self.cue_model.remove,
                translate("ListLayout", "Remove selected cues"),
                self._remove_cues,
            ),
        )
        self.CuesMenu.add(self._edit_actions_group)

        self._media_actions_group = MenuActionsGroup(
            priority=MENU_PRIORITY_CUE + 1
        )
        self._media_actions_group.add(
            SimpleMenuAction(
                translate("CartLayout", "Play"), lambda cue: cue.start()
            ),
            SimpleMenuAction(
                translate("CartLayout", "Pause"), lambda cue: cue.pause()
            ),
            SimpleMenuAction(
                translate("CartLayout", "Stop"), lambda cue: cue.stop()
            ),
        )
        self.CuesMenu.add(self._media_actions_group, MediaCue)

        self._reset_volume_action = SimpleMenuAction(
            translate("CartLayout", "Reset volume"),
            self._reset_cue_volume,
            priority=MENU_PRIORITY_LAYOUT,
        )
        self.CuesMenu.add(self._reset_volume_action, MediaCue)

        self.retranslate()
        self.add_page()

    def retranslate(self):
        self.new_page_action.setText(translate("CartLayout", "Add page"))
        self.new_pages_action.setText(translate("CartLayout", "Add pages"))
        self.rm_current_page_action.setText(
            translate("CartLayout", "Remove current page")
        )
        self.countdown_mode_action.setText(
            translate("CartLayout", "Countdown mode")
        )
        self.show_seek_action.setText(translate("CartLayout", "Show seek-bars"))
        self.show_dbmeter_action.setText(
            translate("CartLayout", "Show dB-meters")
        )
        self.show_volume_action.setText(translate("CartLayout", "Show volume"))
        self.show_accurate_action.setText(
            translate("CartLayout", "Show accurate time")
        )

    def view(self):
        return self._cart_view

    def cue_at(self, index):
        return self._cart_model.item(index)

    def cues(self, cue_type=Cue):
        for cue in self._cart_model:
            if isinstance(cue, cue_type):
                yield cue

    def selected_cues(self, cue_type=Cue):
        for widget in self._widgets():
            if widget.selected and isinstance(widget.cue, cue_type):
                yield widget.cue

    def select_all(self, cue_type=Cue):
        for widget in self._widgets():
            if isinstance(widget.cue, cue_type):
                widget.selected = True

    def deselect_all(self, cue_type=Cue):
        for widget in self._widgets():
            if isinstance(widget.cue, cue_type):
                widget.selected = False

    def invert_selection(self):
        for widget in self._widgets():
            widget.selected = not widget.selected

    def add_pages(self):
        pages, accepted = QInputDialog.getInt(
            self._cart_view,
            translate("CartLayout", "Add pages"),
            translate("CartLayout", "Number of Pages:"),
            value=1,
            min=1,
            max=10,
        )

        if accepted:
            for _ in range(pages):
                self.add_page()

    def add_page(self):
        page = CartPageWidget(self.__rows, self.__columns, self._cart_view)
        page.contextMenuRequested.connect(self.show_context_menu)
        page.moveWidgetRequested.connect(self._move_widget)
        page.copyWidgetRequested.connect(self._copy_widget)

        self._cart_view.addTab(
            page, "Page {}".format(self._cart_view.count() + 1)
        )

    def remove_current_page(self):
        if self._cart_view.count():
            confirm = RemovePageConfirmBox(self._cart_view)

            if confirm.exec() == QMessageBox.Yes:
                self.remove_page(self._cart_view.currentIndex())

    def remove_page(self, index):
        if self._cart_view.count() > index >= 0:
            page = self._page(index)
            page.moveWidgetRequested.disconnect()
            page.copyWidgetRequested.disconnect()

            self._cart_model.remove_page(index)
            self._cart_view.removeTab(index)

            page.deleteLater()

            # Rename every successive tab accordingly
            # TODO: check for "standard" naming using a regex
            text = translate("CartLayout", "Page {number}")
            for n in range(index, self._cart_view.count()):
                self._cart_view.setTabText(n, text.format(number=n + 1))

    @tabs.get
    def _get_tabs(self):
        return self._cart_view.tabTexts()

    @tabs.set
    def _set_tabs(self, texts):
        missing = len(texts) - self._cart_view.count()
        if missing > 0:
            for _ in range(missing):
                self.add_page()

        self._cart_view.setTabTexts(texts)

    @countdown_mode.set
    def _set_countdown_mode(self, enable):
        self.countdown_mode_action.setChecked(enable)
        for widget in self._widgets():
            widget.setCountdownMode(enable)

    @countdown_mode.get
    def _get_countdown_mode(self):
        return self.countdown_mode_action.isChecked()

    @accurate_time.set
    def _set_accurate_time(self, enable):
        self.show_accurate_action.setChecked(enable)
        for widget in self._widgets():
            widget.showAccurateTiming(enable)

    @accurate_time.get
    def _get_accurate_time(self):
        return self.show_accurate_action.isChecked()

    @seek_sliders_visible.set
    def _set_seek_bars_visible(self, visible):
        self.show_seek_action.setChecked(visible)
        for widget in self._widgets():
            widget.showSeekSlider(visible)

    @seek_sliders_visible.get
    def _get_seek_bars_visible(self):
        return self.show_seek_action.isChecked()

    @dbmeters_visible.set
    def _set_dbmeters_visible(self, visible):
        self.show_dbmeter_action.setChecked(visible)
        for widget in self._widgets():
            widget.showDBMeters(visible)

    @dbmeters_visible.get
    def _get_dbmeters_visible(self):
        return self.show_dbmeter_action.isChecked()

    @volume_control_visible.set
    def _set_volume_controls_visible(self, visible):
        self.show_volume_action.setChecked(visible)
        for widget in self._widgets():
            widget.showVolumeSlider(visible)

    @volume_control_visible.get
    def _get_volume_controls_visible(self):
        return self.show_volume_action.isChecked()

    def _key_pressed(self, event):
        self.key_pressed.emit(event)

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
        except (TypeError, ValueError):
            return -1

    def finalize(self):
        # Clean layout menu
        self.app.window.menuLayout.clear()

        # Clean context menu
        self.CuesMenu.remove(self._edit_actions_group)
        self.CuesMenu.remove(self._media_actions_group)
        self.CuesMenu.remove(self._reset_volume_action)

        # Remove reference cycle
        del self._edit_actions_group
        del self._reset_volume_action

    def _widgets(self):
        for page in self._cart_view.pages():
            yield from page.widgets()

    def _page(self, index):
        """:rtype: CartPageWidget"""
        return self._cart_view.widget(index)

    def _move_widget(self, widget, to_row, to_column):
        new_index = self.to_1d_index(
            (self._cart_view.currentIndex(), to_row, to_column)
        )
        self._cart_model.move(widget.cue.index, new_index)

    def _copy_widget(self, widget, to_row, to_column):
        new_index = self.to_1d_index(
            (self._cart_view.currentIndex(), to_row, to_column)
        )
        new_cue = CueFactory.clone_cue(widget.cue)

        self._cart_model.insert(new_cue, new_index)

    def _cue_context_menu(self, position):
        current_page = self._cart_view.currentWidget()
        cue_widget = current_page.widgetAt(current_page.mapFromGlobal(position))

        if cue_widget.selected:
            # If the context menu is requested from a selected cue-widget
            cues = list(self.selected_cues())
        else:
            cues = [cue_widget.cue]

        self.show_cue_context_menu(cues, position)

    def _remove_cue_action(self, cue):
        self._cart_model.remove(cue)

    def _reset_cue_volume(self, cue):
        page, row, column = self.to_3d_index(cue.index)
        widget = self._page(page).widget(row, column)

        widget.resetVolume()

    def _tab_changed(self, index):
        self._cart_model.current_page = index

    def __cue_added(self, cue):
        widget = CueWidget(cue)

        widget.contextMenuRequested.connect(self._cue_context_menu)
        widget.cueExecuted.connect(self.cue_executed.emit)
        widget.editRequested.connect(self.edit_cue)

        widget.showAccurateTiming(self.accurate_time)
        widget.setCountdownMode(self.countdown_mode)
        widget.showVolumeSlider(self.volume_control_visible)
        widget.showDBMeters(self.dbmeters_visible)
        widget.showSeekSlider(self.seek_sliders_visible)

        page, row, column = self.to_3d_index(cue.index)
        if page >= self._cart_view.count():
            self.add_page()

        self._page(page).addWidget(widget, row, column)
        self._cart_view.setCurrentIndex(page)

    def __cue_removed(self, cue):
        page, row, column = self.to_3d_index(cue.index)
        widget = self._page(page).takeWidget(row, column)

        widget.cueExecuted.disconnect()
        widget.contextMenuRequested.disconnect()
        widget.editRequested.disconnect()

        widget.deleteLater()

    def __cue_moved(self, old_index, new_index):
        o_page, o_row, o_column = self.to_3d_index(old_index)
        n_page, n_row, n_column = self.to_3d_index(new_index)

        if o_page == n_page:
            self._page(n_page).moveWidget(o_row, o_column, n_row, n_column)
        else:
            widget = self._page(o_page).takeWidget(o_row, o_column)
            self._page(n_page).addWidget(widget, n_row, n_column)

    def __model_reset(self):
        for page in self._cart_view.pages():
            page.reset()


class RemovePageConfirmBox(QMessageBox):
    def __init__(self, *args):
        super().__init__(*args)

        self.setIcon(self.Question)
        self.setWindowTitle(translate("CartLayout", "Warning"))
        self.setText(
            translate("CartLayout", "Every cue in the page will be lost.")
        )
        self.setInformativeText(
            translate("CartLayout", "Are you sure to continue?")
        )

        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.setDefaultButton(QMessageBox.No)
