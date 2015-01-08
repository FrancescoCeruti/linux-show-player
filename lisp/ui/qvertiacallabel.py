##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5 import QtCore
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QLabel


class QVerticalLabel(QLabel):

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.rotate(-90)

        region = QtCore.QRect(-self.height(), 0, self.height(), self.width())
        hint = painter.drawText(region, self.alignment(), self.text())

        painter.end()

        self.setMaximumWidth(hint.height())
        self.setMinimumWidth(0)
        self.setMaximumHeight(16777215)
        self.setMinimumHeight(hint.width())

    def sizeHint(self):
        return self.size()
