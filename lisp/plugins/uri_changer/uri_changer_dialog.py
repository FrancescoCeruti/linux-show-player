##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *  # @UnusedWildImport

from .session import Session


class UriChangerDialog(QDialog):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.resize(600, 300)
        self.setLayout(QVBoxLayout())

        # FILE SELECT

        self.sessionLayout = QHBoxLayout()
        self.layout().addLayout(self.sessionLayout)

        self.sessionFileEdit = QLineEdit(self)
        self.sessionFileEdit.editingFinished.connect(self.session_init)
        self.sessionLayout.addWidget(self.sessionFileEdit)

        self.sessionFileSelect = QPushButton(self)
        self.sessionFileSelect.clicked.connect(self.session_select)
        self.sessionLayout.addWidget(self.sessionFileSelect)

        self.sessionReload = QPushButton(self)
        self.sessionReload.setIcon(QIcon.fromTheme('view-refresh'))
        self.sessionReload.clicked.connect(self.session_init)
        self.sessionLayout.addWidget(self.sessionReload)

        # REPLACE

        self.replaceLayout = QGridLayout()
        self.layout().addLayout(self.replaceLayout)

        self.currenLabel = QLabel('Current')
        self.currenLabel.setAlignment(Qt.AlignCenter)
        self.replaceLayout.addWidget(self.currenLabel, 0, 0)

        self.replaceLabel = QLabel('Replace')
        self.replaceLabel.setAlignment(Qt.AlignCenter)
        self.replaceLayout.addWidget(self.replaceLabel, 0, 1)

        self.prefixList = QListWidget(self)
        self.prefixList.currentTextChanged.connect(self.prefix_changed)
        self.replaceLayout.addWidget(self.prefixList, 1, 0, 2, 1)

        self.newPrefixLayout = QVBoxLayout()
        self.replaceLayout.addLayout(self.newPrefixLayout, 1, 1)

        self.prefixEdit = QLineEdit(self)
        self.newPrefixLayout.addWidget(self.prefixEdit)
        self.replaceLayout.setAlignment(self.prefixEdit, Qt.AlignTop)

        self.replaceApply = QPushButton(self)
        self.replaceApply.clicked.connect(self.session_replace)
        self.newPrefixLayout.addWidget(self.replaceApply)
        self.newPrefixLayout.setAlignment(self.replaceApply, Qt.AlignRight)

        self.buttons = QDialogButtonBox(self)
        self.buttons.setStandardButtons(QDialogButtonBox.Cancel)
        self.buttons.rejected.connect(self.reject)
        self.layout().addWidget(self.buttons)

        self.saveButton = self.buttons.addButton(QDialogButtonBox.Save)
        self.saveButton.clicked.connect(self.session_save)

        self.retranslateUi()

        self.session = None

    def retranslateUi(self):
        self.sessionFileSelect.setText('Session file')
        self.sessionReload.setToolTip('Reload')
        self.replaceApply.setText('Replace')

    def prefix_changed(self, prefix):
        if self.prefixEdit.text() == '':
            self.prefixEdit.setText(prefix)
        else:
            # Search if the prefixEdit text is one of the listed prefixes
            lower = 0
            upper = self.prefixList.count() - 1
            search = self.prefixEdit.text()

            while lower <= upper:
                middle = (lower + upper) // 2
                item = self.prefixList.item(middle).text()

                if item < search:
                    lower = middle + 1
                elif item > search:
                    upper = middle - 1
                else:
                    self.prefixEdit.setText(prefix)
                    break

    def session_select(self):
        file, _ = QFileDialog.getOpenFileName(self, filter='*.lsp',
                                              directory=os.getenv('HOME'))
        if file != '':
            self.sessionFileEdit.setText(file)
            self.session_init()

    def session_analyze(self):
        self.prefixList.clear()
        self.prefixList.addItems(self.session.analyze())
        self.prefixList.sortItems()

    def session_init(self):
        file = self.sessionFileEdit.text()

        if os.path.exists(file):
            self.session = Session(file)
            self.session_analyze()
        elif file.strip() != '':
            QMessageBox.critical(self, 'Error', 'Session file "' + file + '" not found')

    def session_replace(self):
        self.session.replace(self.prefixList.currentItem().text(),
                             self.prefixEdit.text())
        self.session_analyze()

    def session_save(self):
        file, ok = QFileDialog.getSaveFileName(self, filter='*.lsp',
                                               directory=os.getenv('HOME'))
        if ok:
            self.session.save(file)
            self.accept()
