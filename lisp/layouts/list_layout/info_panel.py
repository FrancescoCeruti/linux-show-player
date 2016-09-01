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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QTextEdit, QLineEdit, QVBoxLayout

from lisp.ui.ui_utils import translate


class InfoPanel(QWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.__cue = None

        # cue name
        self.cueName = QLineEdit(self)
        self.cueName.setFocusPolicy(Qt.NoFocus)
        self.cueName.setReadOnly(True)
        self.layout().addWidget(self.cueName)

        # cue description
        self.cueDescription = QTextEdit(self)
        self.cueDescription.setObjectName('InfoPanelDescription')
        self.cueDescription.setFocusPolicy(Qt.NoFocus)
        self.cueDescription.setReadOnly(True)
        self.layout().addWidget(self.cueDescription)

        self.retranslateUi()

    def retranslateUi(self):
        self.cueName.setPlaceholderText(
            translate('ListLayoutInfoPanel', 'Cue name'))
        self.cueDescription.setPlaceholderText(
            translate('ListLayoutInfoPanel', 'Cue description'))

    def cue_changed(self, cue):
        if self.__cue is not None:
            self.__cue.changed('name').disconnect(self.__name_changed)
            self.__cue.changed('description').disconnect(self.__descr_changed)

        self.__cue = cue

        if self.__cue is not None:
            self.__cue.changed('name').connect(self.__name_changed)
            self.__cue.changed('description').connect(self.__descr_changed)

            self.__name_changed(self.__cue.name)
            self.__descr_changed(self.__cue.description)
        else:
            self.cueName.clear()
            self.cueDescription.clear()

    def __name_changed(self, name):
        self.cueName.setText(str(self.__cue.index) + ' - ' + name)

    def __descr_changed(self, description):
        self.cueDescription.setText(description)
