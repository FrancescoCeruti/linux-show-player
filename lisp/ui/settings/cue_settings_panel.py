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

from collections import OrderedDict
from copy import deepcopy

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPainter, QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter, QSplitterHandle,  QPushButton, QHBoxLayout, QScrollArea

from lisp.cues.cue import Cue
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.settings.settings_page import CueSettingsPage
from lisp.ui.ui_utils import translate
from lisp.ui.widgets import QFoldableTab


class CueSettingsPanelSplitterHandle(QSplitterHandle):

    apply_button_clicked = pyqtSignal()
    """emitted when apply button clicked"""

    def __init__(self, splitter):
        super().__init__(Qt.Vertical, splitter)

        self._panel_current_size = 385
        self.is_fold = True

        self.setFixedHeight(25)

        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 3, 0, 3)
        self.layout().setAlignment(Qt.AlignHCenter)

        self.fold_button = QPushButton()
        self.fold_button.setFocusPolicy(Qt.NoFocus)
        self.fold_button.setFixedWidth(65)
        self.fold_button.setIcon(QIcon.fromTheme('go-up'))
        self.fold_button.setCursor(Qt.ArrowCursor)
        self.fold_button.clicked.connect(self.onFoldButtonClicked)
        self.layout().addWidget(self.fold_button)

        self.apply_button = QPushButton('Apply')
        self.apply_button.setFocusPolicy(Qt.NoFocus)
        self.apply_button.setFixedWidth(65)
        self.apply_button.setCursor(Qt.ArrowCursor)
        self.apply_button.clicked.connect(self.onApplyButtonClicked)
        self.layout().addWidget(self.apply_button)

    def open_panel(self):
        cues_zone, panel_zone = self.splitter().sizes()
        self.splitter().setSizes([cues_zone+panel_zone-self._panel_current_size, self._panel_current_size])
        self.apply_button.show()

    def close_panel(self):
        self._panel_current_size = self.splitter().sizes()[1]
        self.splitter().setSizes([10000, 0])
        self.apply_button.hide()

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


class CueSettingsPanelSplitter(QSplitter):
    """
    This custom QSplitter is intended to work with only two widgets since
    it makes use of `self.handle(0)` which return the handle between widgets 1 and 2
    """
    panel_open = pyqtSignal()
    """emitted when Settings panel open"""
    panel_closed = pyqtSignal()
    """emitted when Settings panel close"""
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
        return self.handle

    def open_settings_panel(self):
        self.handle.open_panel()
        self.panel_open.emit()

    def close_settings_panel(self):
        self.handle.close_panel()
        self.panel_closed.emit()

    def is_panel_open(self):
        return not self.handle.is_fold

    def lazy_init(self):
        """This can only be done when Widgets have been added"""
        self.setCollapsible(0, False)
        self.setCollapsible(1, True)
        #self.close_settings_panel()
        self.open_settings_panel()


class CueSettingsPanel(QWidget):

    def __init__(self, splitter, parent=None):
        super().__init__(parent)

        splitter.apply_button_clicked.connect(self.apply)

        self.setMaximumHeight(600)
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

        # keep trace of tabs with 'type(SettingWidget)':('QFoldableTab', 'SettingWidget')
        self.settings_widgets = OrderedDict()

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

            if issubclass(widget, CueSettingsPage):
                settings_widget = widget(Cue)
            else:
                settings_widget = widget()
            tab = QFoldableTab()
            # Keep easily accessible refs of the pages
            self.settings_widgets[type(settings_widget)] = (tab, settings_widget)
            tab.addTab(settings_widget, translate('SettingsPageName', settings_widget.Name))
            tab.fold()
            tab.hide()
            # insert before stretch
            n = self.scrollWidget.layout().count()
            self.scrollWidget.layout().insertWidget(n-1, tab)

        self.scrollArea.setWidget(self.scrollWidget)

    # TODO : this should be called also when an Undo in MainActionHandler is done, otherwise values don't get updated
    # TODO : this should be called also when the panel opens, since it doesn't update when close
    def display_cue_settings(self, cue=None):
        """
        :param cue: Target cue
        """

        if cue is not None:
            cue_class = cue.__class__
            cue_properties = deepcopy(cue.properties())

        # hide and clear everything
        for tab, widget in self.settings_widgets.values():
            tab.hide()
            widget.clear_settings()

        # show relevant pages, and get settings
        for widget in CueSettingsRegistry().filter(cue_class):
            tab, ret_settings_widget = self.settings_widgets[widget]
            tab.show()
            ret_settings_widget.load_settings(cue_properties)

    def apply(self):
        print('save that shit !!')


