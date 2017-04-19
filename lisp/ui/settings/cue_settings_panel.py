# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
# Copyright 2016-1017 Aurélien Cibrario <aurelien.cibrario@gmail.com>
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

"""
Contain three classes for creating the Cue Settings Panel

A custom of QSplitterHandle and QSplitter to integrate the fold button and logic.
And a custom widget to display and save the Cue Settings
"""

from copy import deepcopy

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPainter, QColor
from PyQt5.QtWidgets import QWidget, QSplitter, QSplitterHandle,  QPushButton,\
    QHBoxLayout, QScrollArea, QLineEdit, QSizePolicy

from lisp.core.actions_handler import MainActionsHandler
from lisp.core.signal import Connection
from lisp.core.singleton import QSingleton
from lisp.core.util import greatest_common_superclass
from lisp.cues.cue import Cue
from lisp.cues.cue_actions import UpdateCueAction, UpdateCuesAction
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.settings.settings_page import CueSettingsPage
from lisp.ui.ui_utils import translate
from lisp.ui.widgets import QFoldableTab


class CueSettingsPanelSplitterHandle(QSplitterHandle):

    panel_opened = pyqtSignal()
    """emitted after Settings panel has open"""
    panel_closed = pyqtSignal()
    """emitted after Settings panel has close"""
    apply_button_clicked = pyqtSignal()
    """emitted when apply button clicked"""

    def __init__(self, splitter):
        super().__init__(Qt.Vertical, splitter)

        self._panel_current_size = 385
        self.is_fold = True

        self.setFixedHeight(25)

        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 3, 0, 3)

        self.cue_name = QLineEdit()
        self.cue_name.setFocusPolicy(Qt.NoFocus)
        policy = QSizePolicy()
        policy.setHorizontalPolicy(QSizePolicy.MinimumExpanding)
        self.cue_name.setSizePolicy(policy)
        self.cue_name.setCursor(Qt.ArrowCursor)
        self.cue_name.selectionChanged.connect(self.cue_name.deselect)
        self.layout().addWidget(self.cue_name)

        self.apply_button = QPushButton('Apply')
        self.apply_button.setFocusPolicy(Qt.NoFocus)
        self.apply_button.setFixedWidth(65)
        self.apply_button.setCursor(Qt.ArrowCursor)
        self.apply_button.clicked.connect(self.onApplyButtonClicked)
        self.layout().addWidget(self.apply_button)
        self.layout().addStretch()

        self.fold_button = QPushButton()
        self.fold_button.setFocusPolicy(Qt.NoFocus)
        self.fold_button.setFixedWidth(65)
        self.fold_button.setIcon(QIcon.fromTheme('go-up'))
        self.fold_button.setCursor(Qt.ArrowCursor)
        self.fold_button.clicked.connect(self.onFoldButtonClicked)
        self.layout().addWidget(self.fold_button)
        self.layout().addStretch()

    def open_panel(self):
        cues_zone, panel_zone = self.splitter().sizes()
        self.splitter().setSizes([cues_zone+panel_zone-self._panel_current_size, self._panel_current_size])
        self.apply_button.show()
        self.cue_name.show()
        self.panel_opened.emit()

    def close_panel(self):
        self._panel_current_size = self.splitter().sizes()[1]
        self.splitter().setSizes([10000, 0])
        self.apply_button.hide()
        self.cue_name.hide()
        self.panel_closed.emit()

    def onFoldButtonClicked(self):
        if self.is_fold:
            self.open_panel()
        else:
            self.close_panel()

    def onApplyButtonClicked(self):
        self.apply_button_clicked.emit()

    def fold_toggled(self):
        self.is_fold = not self.is_fold
        if self.is_fold:
            self.fold_button.setIcon(QIcon.fromTheme('go-up'))
        else:
            self.fold_button.setIcon(QIcon.fromTheme('go-down'))

    def moveEvent(self, event):
        min_panel_height = self.splitter().widget(1).minimumSize().height()
        if self.is_fold and self.splitter().sizes()[1] >= min_panel_height:
            self.fold_toggled()
        elif not self.is_fold and self.splitter().sizes()[1] < min_panel_height:
            self.fold_toggled()

    def paintEvent(self, event):
        # TODO : color value should be taken in style, not hardcoded
        p = QPainter(self)
        col = QColor(58, 58, 58)
        p.fillRect(self.rect(), col)

    def display_cue_name(self, text):
        self.cue_name.setText(text)
        self.cue_name.setSelection(0, 0)


class CueSettingsPanelSplitter(QSplitter):
    """
    This custom QSplitter has been designed to work with two child widgets
    It return CueSettingsPanelSplitterHandle as handle and manage a couple of signals
    """
    panel_opened = pyqtSignal()
    """emitted after Settings panel has open"""
    panel_closed = pyqtSignal()
    """emitted after Settings panel has close"""
    apply_button_clicked = pyqtSignal()
    """emitted when apply button is clicked"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setOrientation(Qt.Vertical)
        self.setHandleWidth(25)

        self.handle = None

    def createHandle(self):
        self.handle = CueSettingsPanelSplitterHandle(self)
        self.handle.apply_button_clicked.connect(lambda: self.apply_button_clicked.emit())
        self.handle.panel_opened.connect(lambda: self.panel_opened.emit())
        self.handle.panel_closed.connect(lambda: self.panel_closed.emit())
        return self.handle

    def open_settings_panel(self):
        self.handle.open_panel()

    def close_settings_panel(self):
        self.handle.close_panel()

    def is_panel_open(self):
        return not self.handle.is_fold

    def lazy_init(self):
        """This can only be done when Widgets have been added"""
        self.setCollapsible(0, False)
        self.setCollapsible(1, True)
        self.close_settings_panel()


class CueSettingsPanel(QWidget, metaclass=QSingleton):

    apply_button_clicked = pyqtSignal(object)
    """emitted when apply button is clicked (list of cues to update)"""

    def __init__(self, splitter):
        super().__init__()

        self.splitter = splitter

        self.setMaximumHeight(350)
        self.setMinimumHeight(100)

        self.setLayout(QHBoxLayout())

        self.scrollWidget = QWidget()
        self.scrollWidget.setLayout(QHBoxLayout())

        stretch_widget = QWidget()
        stretch_widget.setLayout(QHBoxLayout())
        self.scrollWidget.layout().addWidget(stretch_widget)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)

        self.layout().addWidget(self.scrollArea)

        self._current_displayed_cues = None
        self.splitter.apply_button_clicked.connect(self.save_cues_settings)

        self.settings_widgets = {}

        def sk(widget):
            # Sort-Key function
            return translate('SettingsPageName', widget.Name)

        # Extraction of all possible SettingsPages
        cue_pages = sorted(CueSettingsRegistry().filter(Cue), key=sk)
        special_pages = []
        for class_ref, widget in CueSettingsRegistry()._registry.items():
            if class_ref is not Cue:
                special_pages.extend(widget)
        cue_pages.extend(sorted(special_pages, key=sk))

        for widget in cue_pages:

            tab = QFoldableTab()
            # Keep easily accessible refs of the tabs
            self.settings_widgets[widget] = tab
            tab.fold()
            tab.hide()
            # insert before stretch
            n = self.scrollWidget.layout().count()
            self.scrollWidget.layout().insertWidget(n-1, tab)

        self.scrollArea.setWidget(self.scrollWidget)

    def display_cue_settings(self, cues=None):
        """
        Retrieve cues settings and display them in relevant settings pages in Settings Panel
        :param cues : List of cues or None
        """
        # Disconnect previous property_updated signal
        if self._current_displayed_cues is not None:
            if type(self._current_displayed_cues) is list:
                for cue in self._current_displayed_cues:
                    cue.property_updated.disconnect(
                        self.on_cue_properties_updated)
            else:
                self._current_displayed_cues.property_updated.disconnect(
                        self.on_cue_properties_updated)

        self._current_displayed_cues = cues

        # Connect new ones
        if self._current_displayed_cues is not None:
            if type(self._current_displayed_cues) is list:
                for cue in self._current_displayed_cues:
                    cue.property_updated.connect(
                        self.on_cue_properties_updated, mode=Connection.QtQueued)
            else:
                self._current_displayed_cues.property_updated.connect(
                        self.on_cue_properties_updated, mode=Connection.QtQueued)

        # Hide everything
        for tab in self.settings_widgets.values():
            tab.hide()

        # Check if there is multiple cues, and prepare
        if cues is None:
            multiple_cues = False
            cue_properties = {}
            cue_class = Cue
            name_to_display = ''
        elif type(cues) is not list:
            multiple_cues = False
            cue_properties = deepcopy(cues.properties())
            cue_class = cues.__class__
            name_to_display = cues.name
            pass
        elif len(cues) <= 1:
            multiple_cues = False
            cue_properties = deepcopy(cues[0].properties())
            cue_class = cues[0].__class__
            name_to_display = cues[0].name
        else:
            multiple_cues = True
            cue_properties = {}
            cue_class = greatest_common_superclass(cues)
            name_to_display = translate('CueSettingsPanel',
                    'Multiple selection : ') + str([cue.name for cue in cues])

        # Display currently edited cue
        self.splitter.handle.display_cue_name(name_to_display)

        # Load settings in correspondent widgets
        for widget in CueSettingsRegistry().filter(cue_class):
            tab = self.settings_widgets[widget]
            tab.removeTab(0)

            if issubclass(widget, CueSettingsPage):
                settings_widget = widget(cue_class)
            else:
                settings_widget = widget()

            if multiple_cues:
                settings_widget.enable_check(True)

            tab.addTab(settings_widget,
                          translate('CueSettingsPanel', settings_widget.Name))

            settings_widget.load_settings(cue_properties)
            tab.show()

    def on_cue_properties_updated(self):
        self.display_cue_settings(self._current_displayed_cues)
        print(f"display called from on_cue_properties_updated for {self._current_displayed_cues}")

    def save_cues_settings(self):
        aggregated_settings = {}
        for tab in self.settings_widgets.values():
            if tab.isVisible():
                settings = tab.currentWidget().get_settings()
                aggregated_settings = {**aggregated_settings, **settings}

        if type(self._current_displayed_cues) is list:
            action = UpdateCuesAction(aggregated_settings, self._current_displayed_cues)
            MainActionsHandler.do_action(action)
        else:
            action = UpdateCueAction(aggregated_settings, self._current_displayed_cues)
            MainActionsHandler.do_action(action)


