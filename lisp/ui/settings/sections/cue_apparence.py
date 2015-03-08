##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

import re

from PyQt5 import QtCore
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QHBoxLayout, QTextEdit, \
    QSpinBox, QPushButton, QLabel, QColorDialog

from lisp.ui.settings.section import SettingsSection


class Appearance(SettingsSection):

    Name = 'Appearance'

    DEFAULT_STYLE = 'background: rgb(70, 70, 70);' + \
                    'border: 1 solid rgb(0, 0, 0);' + \
                    'border-radius: 6;'

    def __init__(self, size, parent=None):
        super().__init__(size, parent)

        self.verticalLayout = QVBoxLayout(self)

        self.textEditGroup = QGroupBox(self)
        self.horizontalLayout = QHBoxLayout(self.textEditGroup)

        self.textEdit = QTextEdit(self.textEditGroup)
        self.horizontalLayout.addWidget(self.textEdit)

        self.verticalLayout.addWidget(self.textEditGroup)

        self.fontSizeGroup = QGroupBox(self)
        self.horizontalLayout_1 = QHBoxLayout(self.fontSizeGroup)

        self.fontSizeSpin = QSpinBox(self.fontSizeGroup)
        self.horizontalLayout_1.addWidget(self.fontSizeSpin)

        self.verticalLayout.addWidget(self.fontSizeGroup)

        self.colorGroup = QGroupBox(self)
        self.horizontalLayout_2 = QHBoxLayout(self.colorGroup)

        self.colorBButton = QPushButton(self.colorGroup)
        self.horizontalLayout_2.addWidget(self.colorBButton)

        self.colorFButton = QPushButton(self.colorGroup)
        self.horizontalLayout_2.addWidget(self.colorFButton)

        self.verticalLayout.addWidget(self.colorGroup)

        self.previewGroup = QGroupBox(self)
        self.horizontalLayout_3 = QHBoxLayout(self.previewGroup)

        self.beforeLabel = QLabel(self.previewGroup)
        self.beforeLabel.setStyleSheet(self.DEFAULT_STYLE)
        self.beforeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.horizontalLayout_3.addWidget(self.beforeLabel)

        self.nowLabel = QLabel(self.previewGroup)
        self.nowLabel.setStyleSheet(self.DEFAULT_STYLE)
        self.nowLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.horizontalLayout_3.addWidget(self.nowLabel)

        self.verticalLayout.addWidget(self.previewGroup)

        self.textEdit.textChanged.connect(self.changeText)
        self.fontSizeSpin.valueChanged.connect(self.updatePreview)
        self.colorBButton.clicked.connect(self.changeBColor)
        self.colorFButton.clicked.connect(self.changeFColor)

        self.warning = QLabel(self)
        self.warning.setText("The real appearance depends on the layout")
        self.warning.setAlignment(QtCore.Qt.AlignCenter)
        self.warning.setStyleSheet("color: red; font-weight: bold")

        self.verticalLayout.addWidget(self.warning)

        self.verticalLayout.setStretch(0, 3)
        self.verticalLayout.setStretch(1, 1)
        self.verticalLayout.setStretch(2, 1)
        self.verticalLayout.setStretch(3, 2)
        self.verticalLayout.setStretch(4, 1)

        self.retranslateUi()

        self.bColor = 'rgb(0,0,0)'
        self.fColor = 'rgb(177,177,177)'
        self.fontSizeSpin.setValue(11)

    def retranslateUi(self):
        self.textEditGroup.setTitle("Shown Text")
        self.textEdit.setText("Empty")
        self.fontSizeGroup.setTitle("Set Font Size")
        self.colorGroup.setTitle("Color")
        self.colorBButton.setText("Select background color")
        self.colorFButton.setText("Select font color")
        self.previewGroup.setTitle("Preview")
        self.beforeLabel.setText("Before")
        self.nowLabel.setText("After")

    def enable_check(self, enable):
        self.textEditGroup.setCheckable(enable)
        self.textEditGroup.setChecked(False)

        self.fontSizeGroup.setCheckable(enable)
        self.fontSizeGroup.setChecked(False)

        self.colorGroup.setCheckable(enable)
        self.colorGroup.setChecked(False)

    def get_configuration(self):
        conf = {}

        checked = self.textEditGroup.isCheckable()

        if(not (checked and not self.textEditGroup.isChecked())):
            conf['name'] = self.textEdit.toPlainText()
        if(not (checked and not self.colorGroup.isChecked())):
            conf['background'] = self.bColor
            conf['color'] = self.fColor
        if(not (checked and not self.fontSizeGroup.isChecked())):
            conf['font-size'] = self.fontSizeSpin.value()

        return conf

    def set_configuration(self, conf):
        if(conf is not None):
            if('name' in conf):
                self.textEdit.setText(conf['name'])
                self.nowLabel.setText(conf['name'])
            if('background' in conf):
                self.bColor = conf['background']
            if('color' in conf):
                self.fColor = conf['color']
            if('font-size' in conf):
                self.fontSizeSpin.setValue(conf['font-size'])

            self.updatePreview()
            self.beforeLabel.setStyleSheet(self.nowLabel.styleSheet())

    def updatePreview(self):
        self.nowLabel.setStyleSheet('background: ' + self.bColor + ';\
                     border: 1 solid rgb(0,0,0);\
                     border-radius: 6;\
                     color: ' + self.fColor + ';\
                     font-size: ' + str(self.fontSizeSpin.value()) + 'pt;')

    def changeBColor(self):
        initial = QColor(*map(int, re.findall('\d{1,3}', self.bColor)))
        color = QColorDialog.getColor(initial, parent=self)

        if(color.isValid()):
            self.bColor = 'rgb' + str(color.getRgb())
            self.updatePreview()

    def changeFColor(self):
        initial = QColor(*map(int, re.findall('\d{1,3}', self.fColor)))
        color = QColorDialog.getColor(initial, parent=self)

        if(color.isValid()):
            self.fColor = 'rgb' + str(color.getRgb())
            self.updatePreview()

    def changeText(self):
        self.nowLabel.setText(self.textEdit.toPlainText())
