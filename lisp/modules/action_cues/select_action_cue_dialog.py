# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
# Copyright 2012-2016 Aurélien Cibrario <aurelien.cibrario@gmail.com>
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

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QGroupBox, QDialogButtonBox

from lisp.ui.ui_utils import translate

class SelectActionCueDialog(QDialog):

    LastActionCueChoice = ''

    def __init__(self, available_cues, **kwargs):
        super().__init__(**kwargs)

        self.setLayout(QVBoxLayout())
        self.groupBox = QGroupBox()
        self.groupBox.setLayout(QVBoxLayout())
        self.groupBox.setTitle(translate('MainWindows', 'Select new Action Cue'))

        self.layout().addWidget(self.groupBox)

        self.cuesComboBox = QComboBox()
        self.groupBox.layout().addWidget(self.cuesComboBox)

        self.dialogButtons = QDialogButtonBox(self)
        self.dialogButtons.setStandardButtons(QDialogButtonBox.Cancel |
                                              QDialogButtonBox.Ok)
        self.layout().addWidget(self.dialogButtons)

        self.dialogButtons.rejected.connect(self.reject)
        self.dialogButtons.accepted.connect(self.accept)

        for cue_name, add_func in available_cues.items():
            self.cuesComboBox.addItem(
                translate('CueName', cue_name))

        self.cuesComboBox.setCurrentText(self.LastActionCueChoice)

    def accept(self):
        self.__class__.LastActionCueChoice = self.cuesComboBox.currentText()
        super().accept()

