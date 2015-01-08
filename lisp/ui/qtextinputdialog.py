##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5 import QtCore
from PyQt5.QtWidgets import *  # @UnusedWildImport


class QTextInputDialog(QDialog):

    def __init__(self, initial='', parent=None):
        super().__init__(parent)

        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setMaximumSize(400, 230)
        self.setMinimumSize(400, 230)
        self.resize(400, 230)

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setGeometry(QtCore.QRect(5, 5, 390, 190))
        self.scrollArea.setWidgetResizable(True)

        self.plainTextEdit = QPlainTextEdit()
        self.plainTextEdit.setGeometry(QtCore.QRect(0, 0, 390, 190))
        self.plainTextEdit.setPlainText(initial)

        self.scrollArea.setWidget(self.plainTextEdit)

        self.acceptButton = QPushButton(self)
        self.acceptButton.setGeometry(QtCore.QRect(280, 200, 100, 25))
        self.acceptButton.setText("Ok")

        self.rejectButton = QPushButton(self)
        self.rejectButton.setGeometry(QtCore.QRect(160, 200, 100, 25))
        self.rejectButton.setText("Cancel")

        self.rejectButton.clicked.connect(self.reject)
        self.acceptButton.clicked.connect(self.accept)
