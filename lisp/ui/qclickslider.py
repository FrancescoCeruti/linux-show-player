##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QStyle, QSlider, QStyleOptionSlider


class QClickSlider(QSlider):

    sliderJumped = pyqtSignal(int)

    def mousePressEvent(self, e):
        cr = self._control_rect()

        if e.button() == Qt.LeftButton and not cr.contains(e.pos()):
            # Set the value to the minimum
            value = self.minimum()
            # zmax is the maximum value starting from zero
            zmax = self.maximum() - self.minimum()

            if self.orientation() == Qt.Vertical:
                # Add the current position multiplied for value/size ratio
                value += (self.height() - e.y()) * (zmax / self.height())
            else:
                value += e.x() * (zmax / self.width())

            if self.value() != value:
                self.setValue(value)
                self.sliderJumped.emit(self.value())
                e.accept()
            else:
                e.ignore()
        else:
            super().mousePressEvent(e)

    def _control_rect(self):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)

        return self.style().subControlRect(QStyle.CC_Slider, opt,
                                           QStyle.SC_SliderHandle)
