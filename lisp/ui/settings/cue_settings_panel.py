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
from PyQt5.QtWidgets import QWidget, QSplitter, QSplitterHandle,  QPushButton,\
    QHBoxLayout, QScrollArea, QLineEdit, QSizePolicy

from lisp.core.util import greatest_common_superclass
from lisp.cues.cue import Cue
from lisp.layouts.cue_layout import CueLayout
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
        #self.layout().setAlignment(Qt.AlignHCenter)

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
    This custom QSplitter is intended to work with only two widgets since
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
        #self.close_settings_panel()
        self.open_settings_panel()


class CueSettingsPanel(QWidget):

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

        self._cues_to_update = []

        # TODO : Start here to record settings
        #self.splitter.apply_button_clicked.connect(
        #    lambda: self.apply_button_clicked(self._cues_to_update))
        # keep trace of tabs with 'type(SettingWidget)':('QFoldableTab', 'SettingWidget')

        # FIXME : is orderedDict still needed ?
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
    def display_cue_settings(self, cues=None):
        """
        Retrieve cues settings and display them in relevant settings pages in Settings Panel
        :param cues : List of cues or None
        """

        # Hide and clear everything
        for tab, widget in self.settings_widgets.values():
            tab.hide()
            widget.enable_check(False)
            widget.clear_settings()

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

        # Load settings in correspondant widgets
        for page in CueSettingsRegistry().filter(cue_class):
            tab, widget = self.settings_widgets[page]
            if multiple_cues:
                widget.enable_check(True)
            widget.load_settings(cue_properties)
            tab.show()

