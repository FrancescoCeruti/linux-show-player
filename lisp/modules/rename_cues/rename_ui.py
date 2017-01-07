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

from os import cpu_count

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QRadioButton, QSpinBox, \
    QCheckBox, QFrame, QLabel, QGridLayout, QButtonGroup, QProgressDialog, QLineEdit

from lisp.ui.ui_utils import translate
from lisp.application import Application


class RenameUi(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowModality(Qt.ApplicationModal)
        self.setMaximumSize(380, 210)
        self.setMinimumSize(380, 210)
        self.resize(380, 210)

        self.setLayout(QGridLayout())


        # Preview label
        self.previewLabel = QLabel(self)
        self.previewLabel.setText('Preview :')
        self.layout().addWidget(self.previewLabel, 0, 0)
        self.previewEdit = QLineEdit(self)
        self.previewEdit.setReadOnly(True)
        self.layout().addWidget(self.previewEdit, 0, 1)

        # Options checkbox
        self.capitalizeBox = QCheckBox(self)
        self.capitalizeBox.toggled.connect(self.capitalize_cue_name)
        self.layout().addWidget(self.capitalizeBox, 1, 0)
        self.capitalizeLabel = QLabel(self)
        self.capitalizeBox.setText('Capitalize')
        self.layout().addWidget(self.capitalizeLabel, 1, 1)

        self.lowerBox = QCheckBox(self)
        self.lowerBox.toggled.connect(self.lower_cue_name)
        self.layout().addWidget(self.lowerBox, 2, 0)
        self.lowerLabel = QLabel(self)
        self.lowerLabel.setText('Lowercase')
        self.layout().addWidget(self.lowerLabel, 2, 1)

        # OK / Cancel buttons
        self.dialogButtons = QDialogButtonBox(self)
        self.dialogButtons.setStandardButtons(QDialogButtonBox.Ok |
                                              QDialogButtonBox.Cancel)
        self.layout().addWidget(self.dialogButtons, 5, 0, 1, 2)

        self.dialogButtons.accepted.connect(self.accept)
        self.dialogButtons.rejected.connect(self.reject)


        self.retranslateUi()

        self.get_cues_name()


    def retranslateUi(self):
        #TODO : translation file & Co
        self.setWindowTitle(
            translate('RenameCues', 'Rename cues'))

    def get_cues_name(self):
        cues = Application().layout.get_selected_cues()
        if cues != []:
            # FIXME : Récupère juste le premier pour le test
            self.previewEdit.setText('{}'.format(cues[0].name))

    def capitalize_cue_name(self):
        if self.capitalizeBox.isChecked():
            self.previewEdit.setText(self.previewEdit.text().upper())

    def lower_cue_name(self):
        if self.lowerBox.isChecked():
            self.previewEdit.setText(self.previewEdit.text().lower())


# class GainProgressDialog(QProgressDialog):
#     def __init__(self, maximum, parent=None):
#         super().__init__(parent)
#
#         self.setWindowModality(Qt.ApplicationModal)
#         self.setWindowTitle(translate('ReplayGain', 'Processing files ...'))
#         self.setMaximumSize(320, 110)
#         self.setMinimumSize(320, 110)
#         self.resize(320, 110)
#
#         self.setMaximum(maximum)
#         self.setLabelText('0 / {0}'.format(maximum))
#
#     def on_progress(self, value):
#         if value == -1:
#             # Hide the progress dialog
#             self.setValue(self.maximum())
#             self.deleteLater()
#         else:
#             self.setValue(self.value() + value)
#             self.setLabelText('{0} / {1}'.format(self.value(), self.maximum()))
