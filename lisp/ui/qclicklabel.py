##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5.QtCore import pyqtSignal, QEvent
from PyQt5.QtWidgets import QLabel


class QClickLabel(QLabel):

    clicked = pyqtSignal(QEvent)

    def __init(self, parent):
        super().__init__(parent)

    def mouseReleaseEvent(self, e):
        if(self.contentsRect().contains(e.pos())):
            self.clicked.emit(e)
