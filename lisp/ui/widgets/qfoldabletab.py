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
Custom QTabWidget. Has hability to "fold"
"""

from copy import deepcopy

from PyQt5.QtWidgets import qApp, QWidget, QVBoxLayout, QSplitter, QSplitterHandle,  QPushButton, QTabWidget, \
    QHBoxLayout, QTextEdit, QScrollArea, QFrame, QLineEdit, QSpinBox, QCheckBox, QTimeEdit
from PyQt5.QtGui import QIcon, QPainter, QColor
from PyQt5.QtCore import pyqtSignal, Qt, QRect, QObject, QEvent

from lisp.layouts.cue_layout import CueMenuRegistry
from lisp.ui.settings.cue_settings import CueSettingsRegistry, CueSettings
from lisp.cues.cue import Cue
from lisp.ui.settings.settings_page import CueSettingsPage, SettingsPage
from lisp.ui.ui_utils import translate


class QFoldableTab(QTabWidget):


    def fold(self):
        self.setDisabled(True)

    def unfold(self):
        self.setDisabled(False)
