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

import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QComboBox, QPushButton, QFrame, QTextBrowser, QFileDialog, QGridLayout

from lisp import layouts
from lisp.ui.ui_utils import translate


class LayoutSelect(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.filepath = ''

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle(translate('LayoutSelect', 'Layout selection'))
        self.setMaximumSize(675, 300)
        self.setMinimumSize(675, 300)
        self.resize(675, 300)

        self.setLayout(QGridLayout(self))
        self.layout().setContentsMargins(5, 5, 5, 5)

        self.layoutCombo = QComboBox(self)
        self.layoutCombo.currentIndexChanged.connect(self.show_description)
        self.layout().addWidget(self.layoutCombo, 0, 0)

        self.confirmButton = QPushButton(self)
        self.confirmButton.setText(translate('LayoutSelect', 'Select layout'))
        self.layout().addWidget(self.confirmButton, 0, 1)

        self.fileButton = QPushButton(self)
        self.fileButton.setText(translate('LayoutSelect', 'Open file'))
        self.layout().addWidget(self.fileButton, 0, 2)

        self.layout().setColumnStretch(0, 3)
        self.layout().setColumnStretch(1, 2)
        self.layout().setColumnStretch(2, 1)

        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.layout().addWidget(line, 1, 0, 1, 3)

        self.description = QTextBrowser(self)
        self.layout().addWidget(self.description, 2, 0, 1, 3)

        for layout_class in layouts.get_layouts():
            self.layoutCombo.addItem(layout_class.NAME, layout_class)

        if self.layoutCombo.count() == 0:
            raise Exception('No layout installed!')

        self.confirmButton.clicked.connect(self.accept)
        self.fileButton.clicked.connect(self.open_file)

    def selected(self):
        return self.layoutCombo.currentData()

    def show_description(self, index):
        layout = self.layoutCombo.currentData()

        details = '<ul>'
        for detail in layout.DETAILS:
            details += '<li>' + translate('LayoutDetails', detail)
        details += '</ul>'

        self.description.setHtml(
            '<center><h2>' + layout.NAME + '</h2>'
            '<i><h4>' + translate('LayoutDescription', layout.DESCRIPTION) +
            '</h4></i></center>' + details)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, filter='*.lsp',
                                              directory=os.getenv('HOME'))
        self.filepath = path
        self.accept()
