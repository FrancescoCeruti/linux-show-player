##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QComboBox, \
    QPushButton, QFrame, QTextBrowser, QFileDialog
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

        self.vLayout = QVBoxLayout(self)
        self.vLayout.setContentsMargins(5, 5, 5, 5)

        self.hLayout = QHBoxLayout(self)
        self.vLayout.addLayout(self.hLayout)

        self.layoutBox = QComboBox(self)
        self.hLayout.addWidget(self.layoutBox)

        self.layButton = QPushButton(self)
        self.layButton.setText('Select layout')
        self.hLayout.addWidget(self.layButton)

        self.fileButton = QPushButton(self)
        self.fileButton.setText('Open file')
        self.hLayout.addWidget(self.fileButton)

        self.hLayout.setStretch(0, 3)
        self.hLayout.setStretch(1, 2)
        self.hLayout.setStretch(2, 1)

        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.vLayout.addWidget(line)

        self.description = QTextBrowser(self)
        self.vLayout.addWidget(self.description)

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
