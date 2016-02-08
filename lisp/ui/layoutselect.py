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


class LayoutSelect(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.filepath = ''
        self.layouts = {}

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle('Layout selection')
        self.setMaximumSize(675, 300)
        self.setMinimumSize(675, 300)
        self.resize(675, 300)

        self.setLayout(QGridLayout(self))
        self.layout().setContentsMargins(5, 5, 5, 5)

        self.layoutBox = QComboBox(self)
        self.layout().addWidget(self.layoutBox, 0, 0)

        self.layButton = QPushButton(self)
        self.layButton.setText('Select layout')
        self.layout().addWidget(self.layButton, 0, 1)

        self.fileButton = QPushButton(self)
        self.fileButton.setText('Open file')
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
            self.layoutBox.addItem(layout_class.NAME)
            self.layouts[layout_class.NAME] = (layout_class,
                                               layout_class.DESCRIPTION)

        if self.layoutBox.count() == 0:
            raise Exception('No layout installed!')
        self.show_description(self.layoutBox.currentText())

        self.layoutBox.currentTextChanged.connect(self.show_description)
        self.layButton.clicked.connect(self.accept)
        self.fileButton.clicked.connect(self.open_file)

    def slected(self):
        return self.layouts[self.layoutBox.currentText()][0]

    def show_description(self, layout_name):
        self.description.setHtml('<center><h2>' + layout_name +
                                 '</h2></center><br>' +
                                 self.layouts[layout_name][1])

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, filter='*.lsp',
                                              directory=os.getenv('HOME'))
        self.filepath = path
        self.accept()

    def closeEvent(self, e):
        e.ignore()
