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
And a custom widget to display the Cue Settings
"""

from copy import deepcopy

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter, QSplitterHandle,  QPushButton, QTabWidget, \
    QHBoxLayout, QTextEdit
from PyQt5.QtGui import QIcon, QPainter, QColor
from PyQt5.QtCore import Qt, QRect

from lisp.layouts.cue_layout import CueMenuRegistry
from lisp.ui.settings.cue_settings import CueSettingsRegistry, CueSettings
from lisp.cues.cue import Cue
from lisp.ui.settings.settings_page import CueSettingsPage
from lisp.ui.ui_utils import translate



class CueSettingsPanelSplitterHandle(QSplitterHandle):
    def __init__(self, splitter):
        super().__init__(Qt.Vertical, splitter)

        self._panel_max_size = 500
        self._panel_current_size = 400
        self.is_fold = True

        self.setFixedHeight(25)

        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 3, 0, 3)
        self.layout().setAlignment(Qt.AlignHCenter)

        self.fold_button = QPushButton()
        self.fold_button.setFocusPolicy(Qt.NoFocus)
        self.fold_button.setFixedWidth(65)
        self.fold_button.setIcon(QIcon.fromTheme('go-up'))
        self.fold_button.setCursor(Qt.ArrowCursor)
        self.fold_button.clicked.connect(self.onFoldButtonClicked)
        self.layout().addWidget(self.fold_button)

    def open_panel(self, max_size = False):
        if max_size:
            self._panel_current_size = self._panel_max_size
        cues_zone, panel_zone = self.splitter().sizes()
        self.splitter().setSizes([cues_zone+panel_zone-self._panel_current_size, self._panel_current_size])

    def close_panel(self):
        self._panel_current_size = self.splitter().sizes()[1]
        self.splitter().setSizes([10000, 0])

    def onFoldButtonClicked(self):
        if self.is_fold:
            self.open_panel()
        else:
            self.close_panel()

    def fold_toggled(self):
        self.is_fold = not self.is_fold
        if self.is_fold:
            self.fold_button.setIcon(QIcon.fromTheme('go-up'))
        else:
            self.fold_button.setIcon(QIcon.fromTheme('go-down'))

    def moveEvent(self, event):
        min_panel_height = self.splitter().widget(1).minimumSize().height()
        if(self.is_fold and self.splitter().sizes()[1] >= min_panel_height):
            self.fold_toggled()
        elif(not self.is_fold and self.splitter().sizes()[1] < min_panel_height):
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

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setOrientation(Qt.Vertical)
        self.setHandleWidth(25)

    def createHandle(self):
        handle = CueSettingsPanelSplitterHandle(self)
        return handle

    def lazy_init(self):
        """This can only be done when Widgets have been added"""
        self.setCollapsible(0, False)
        self.setCollapsible(1, True)
        #self.handle(0).onFoldButtonClicked()

    def open_settings_panel(self, max_size = False):
        handle = self.handle(0)
        handle.open_panel()

class CueSettingsPanel(QWidget):

    def __init__(self, parent= None):
        super().__init__(parent)

        self.setMaximumHeight(600)
        self.setMinimumHeight(100)

        self.setLayout(QHBoxLayout())

        self.info = QTextEdit()
        self.layout().addWidget(self.info)

        # TODO : could settings be automatically saved when widget loose focus ?
        # TODO : Playing a cue does imply panel loosing focus ?


    def display_cue(self, cue = None, cue_class = None):
        """
        :param cue: Target cue, or None for multi-editing
        :param cue_class: when cue is None, used to specify the reference class
        """

        # Delete all widgets present in layout
        for i in reversed(range(self.layout().count())):
            self.layout().itemAt(i).widget().setParent(None)

        if cue is not None:
            cue_class = cue.__class__
            cue_properties = deepcopy(cue.properties())
            self.setWindowTitle(cue_properties['name'])
        else:
            cue_properties = {}
            if cue_class is None:
                cue_class = Cue

        def sk(widget):
            # Sort-Key function
            return translate('SettingsPageName', widget.Name)

        for widget in sorted(CueSettingsRegistry().filter(cue_class), key=sk):
            if issubclass(widget, CueSettingsPage):
                settings_widget = widget(cue_class)
            else:
                settings_widget = widget()

            self.layout().addWidget(settings_widget)
