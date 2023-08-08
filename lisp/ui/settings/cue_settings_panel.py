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

    def __init__(self, splitter):
        super().__init__(Qt.Vertical, splitter)

        self._panel_current_size = 150
        self.is_fold = True

        self.setFixedHeight(25)

        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(6, 3, 6, 3)

        self.cue_name = QLineEdit()
        self.cue_name.setFocusPolicy(Qt.NoFocus)
        policy = QSizePolicy()
        policy.setHorizontalPolicy(QSizePolicy.MinimumExpanding)
        self.cue_name.setSizePolicy(policy)
        self.cue_name.setCursor(Qt.ArrowCursor)
        self.cue_name.hide()
        self.cue_name.selectionChanged.connect(self.cue_name.deselect)
        self.layout().addWidget(self.cue_name)

        self.apply_button = QPushButton(
            translate('CueSettingsPanel', 'Apply'))
        self.apply_button.setFocusPolicy(Qt.NoFocus)
        self.apply_button.setFixedWidth(65)
        self.apply_button.setCursor(Qt.ArrowCursor)
        self.apply_button.hide()
        self.apply_button.clicked.connect(self.splitter().onApplyButtonClicked)
        self.layout().addWidget(self.apply_button)
        self.layout().addStretch()

        self.fold_button = QPushButton()
        self.fold_button.setFocusPolicy(Qt.NoFocus)
        self.fold_button.setFixedWidth(65)
        self.fold_button.setCursor(Qt.ArrowCursor)
        self.fold_button.setIcon(QIcon.fromTheme('go-up'))
        self.fold_button.clicked.connect(self.splitter().onFoldButtonClicked)
        self.layout().addWidget(self.fold_button)
        self.layout().addStretch()

    def toggle_fold(self):
        if self.is_fold:
            cues_zone, panel_zone = self.splitter().sizes()
            self.splitter().setSizes(
                [cues_zone+panel_zone-self._panel_current_size, self._panel_current_size])
        else:
            self._panel_current_size = self.splitter().sizes()[1]
            self.splitter().setSizes([10000, 0])

    def on_fold(self):
        self.fold_button.setIcon(QIcon.fromTheme('go-up'))
        self.apply_button.hide()
        self.cue_name.hide()

    def on_unfold(self):
        self.fold_button.setIcon(QIcon.fromTheme('go-down'))
        self.apply_button.show()
        self.cue_name.show()
        self.splitter().panel_opened.emit()

    def adjust_height(self):
        pref_height = self.splitter().widget(1).preferred_height()
        # Take margins into account
        pref_height += 10
        cues_zone, panel_zone = self.splitter().sizes()
        self.splitter().setSizes(
            [cues_zone+panel_zone-pref_height, pref_height])

    def display_cue_name(self, text):
        self.cue_name.setText(text)
        self.cue_name.setSelection(0, 0)

    def moveEvent(self, event):
        min_panel_height = self.splitter().widget(1).minimumSize().height()
        if self.is_fold and self.splitter().sizes()[1] >= min_panel_height:
            self.is_fold = False
            self.on_unfold()
        elif not self.is_fold and self.splitter().sizes()[1] < min_panel_height:
            self.is_fold = True
            self.on_fold()

    def paintEvent(self, event):
        # TODO : color value should be taken in style, not hardcoded
        p = QPainter(self)
        col = QColor(58, 58, 58)
        p.fillRect(self.rect(), col)


class CueSettingsPanelSplitter(QSplitter):

    panel_opened = pyqtSignal()
    """emitted when panel opens"""
    apply_button_clicked = pyqtSignal()
    """emitted when apply button is clicked"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setOrientation(Qt.Vertical)
        self.setHandleWidth(25)

        self.handle = None

    def createHandle(self):
        self.handle = CueSettingsPanelSplitterHandle(self)
        return self.handle

    def onApplyButtonClicked(self):
        self.apply_button_clicked.emit()

    def onFoldButtonClicked(self):
        self.handle.toggle_fold()

    def open_settings_panel(self):
        self.handle.open_panel()

    def close_settings_panel(self):
        self.handle.close_panel()

    def is_panel_open(self):
        return not self.handle.is_fold

    def lazy_init(self):
        """
        Ui initialisation
        This can only be done when Widgets have been added
        """
        self.setCollapsible(0, False)
        self.setCollapsible(1, True)
        self.setSizes([10000, 0])


class CueSettingsPanel(QWidget, metaclass=QSingleton):

    def __init__(self, splitter):
        super().__init__()

        self.splitter = splitter

        self.setMinimumHeight(150)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.scrollWidget = QSplitter()
        self.scrollWidget.setChildrenCollapsible(False)
        self.scrollWidget.setContentsMargins(8, 5, 8, 0)

        stretch_widget = QWidget()
        stretch_widget.setLayout(QHBoxLayout())
        self.scrollWidget.addWidget(stretch_widget)

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
            tab.fold_toggled.connect(self.splitter.handle.adjust_height)
            tab.fold_toggled.connect(self.adjust_page_width)
            # Keep easily accessible refs of the tabs
            self.settings_widgets[widget] = tab
            tab.fold()
            tab.hide()
            # insert before stretch
            n = self.scrollWidget.count()
            self.scrollWidget.insertWidget(n-1, tab)

        self.scrollArea.setWidget(self.scrollWidget)
        self.adjust_page_width()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.save_cues_settings()

    def display_cue_settings(self, cues=None):
        """
        Retrieve cues settings and display them in relevant settings pages in Settings Panel
        :param cues : List of Cues or Cue or None
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
        if self._current_displayed_cues is not None:
            aggregated_settings = {}
            for tab in self.settings_widgets.values():
                if tab.isVisible():
                    settings = tab.currentWidget().get_settings()
                    aggregated_settings = {**aggregated_settings, **settings}

            if type(self._current_displayed_cues) is list:
                self._current_displayed_cues.property_updated.disconnect(self.on_cue_properties_updated)
                action = UpdateCuesAction(aggregated_settings, self._current_displayed_cues)
                MainActionsHandler.do_action(action)
                self._current_displayed_cues.property_updated.connect(
                    self.on_cue_properties_updated, mode=Connection.QtQueued)
            else:
                self._current_displayed_cues.property_updated.disconnect(self.on_cue_properties_updated)
                action = UpdateCueAction(aggregated_settings, self._current_displayed_cues)
                MainActionsHandler.do_action(action)
                self._current_displayed_cues.property_updated.connect(
                    self.on_cue_properties_updated, mode=Connection.QtQueued)

    def preferred_height(self):
        """
        Return prefered height based on custom hints given by QFoldableTab
        :return: int
        """
        pref_height = 0
        for tab in self.settings_widgets.values():
            height = tab.sizeHint().height()
            if height > pref_height:
                pref_height = height
        return pref_height

    def adjust_page_width(self):
        """Give maximum space to the last widget (spacer)"""
        pass
        sizes = [0 for i in range(self.scrollWidget.count()-1)]
        sizes.append(10000)
        # sizes = self.scrollWidget.sizes()
        # sizes[-1] = 10000
        self.scrollWidget.setSizes(sizes)

