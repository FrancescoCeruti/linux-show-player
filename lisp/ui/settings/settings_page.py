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

from PyQt5.QtWidgets import QWidget, QLineEdit, QTextEdit, QSpinBox, QTimeEdit, QListWidget
from PyQt5.QtCore import pyqtSignal

from lisp.ui.qmodels import SimpleTableModel

class SettingsPage(QWidget):
    Name = 'Page'
    MinHeight = 350
    MinWidth = 400

    # TODO : will be useful for auto-recording
    modified = pyqtSignal(object, object)
    """Emitted when a setting as been modified (SettingsPage, sender_widget)"""

    def enable_check(self, enabled):
        """Enable option check"""

    def get_settings(self):
        """Return the current settings."""
        return {}

    def load_settings(self, settings):
        """Load the settings."""

    def clear_settings(self):
        """
        Clear Settings inputs.
        Needs to be completed when subclasses make use of non standard widgets, lists, etc..
        """
        for w in self.findChildren((QLineEdit, QTextEdit, QSpinBox,
                        QTimeEdit, QListWidget)):
            w.clear()

    def prepare_for_load(self, cue_class):
        """
        Useful for preparing sub pages or input widget how depends on edited
        Cue classes, or other special initialization
        :param cue_class: Cue.__class__
        """

class CueSettingsPage(SettingsPage):
    Name = 'Cue page'

    def __init__(self, cue_class, **kwargs):
        super().__init__(**kwargs)

        self._cue_class = cue_class
