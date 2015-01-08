##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5 import QtCore
from PyQt5.QtGui import QLinearGradient, QColor, QPainter
from PyQt5.QtWidgets import QWidget
from lisp.utils.configuration import config


class QDbMeter(QWidget):

    DB_MIN = int(config["DbMeter"]["dbMin"])
    DB_MAX = int(config["DbMeter"]["dbMax"])
    DB_CLIP = int(config["DbMeter"]["dbClip"])

    def __init__(self, parent):
        super().__init__(parent)

        self.grad = QLinearGradient()
        self.grad.setColorAt(0, QColor(0, 255, 0))         # Green
        self.grad.setColorAt(0.5, QColor(255, 255, 0))     # Yellow
        self.grad.setColorAt(1, QColor(255, 0, 0))         # Red

        self.reset()

    def reset(self):
        self.peaks = [self.DB_MIN, self.DB_MIN]
        self.rmss = [self.DB_MIN, self.DB_MIN]
        self.decPeak = [self.DB_MIN, self.DB_MIN]
        self.clipping = {}
        self.repaint()

    @QtCore.pyqtSlot(list, list, list)
    def plot(self, peaks, rms, decPeak):
        if(len(peaks) == 1):
            self.peaks = peaks * 2
            self.rmss = rms * 2
            self.decPeak = decPeak * 2
        else:
            self.peaks = peaks
            self.rmss = rms
            self.decPeak = decPeak

        self.repaint()

    def paintEvent(self, e):
        if not self.visibleRegion().isEmpty():
            # Stretch factor
            mul = (self.height() - 4)
            mul /= (self.DB_MAX - self.DB_MIN)

            peaks = []
            for n, peak in enumerate(self.peaks):
                if peak > self.DB_CLIP:
                    self.clipping[n] = True

                if peak < self.DB_MIN:
                    peak = self.DB_MIN
                elif peak > self.DB_MAX:
                    peak = self.DB_MAX

                peaks.append(round((peak - self.DB_MIN) * mul))

            rmss = []
            for n, rms in enumerate(self.rmss):
                if rms < self.DB_MIN:
                    rms = self.DB_MIN
                elif rms > self.DB_MAX:
                    rms = self.DB_MAX

                rmss.append(round((rms - self.DB_MIN) * mul))

            decPeaks = []
            for decPeak in self.decPeak:
                if decPeak < self.DB_MIN:
                    decPeak = self.DB_MIN
                elif decPeak > self.DB_MAX:
                    decPeak = self.DB_MAX

                decPeaks.append(round((decPeak - self.DB_MIN) * mul))

            qp = QPainter()
            qp.begin(self)
            qp.setBrush(QColor(0, 0, 0, 0))

            xpos = 0
            xdim = self.width() / len(peaks)

            for n in range(len(peaks)):
                peak = peaks[n]
                rms = rmss[n]
                decPeak = decPeaks[n]

                # Maximum "peak-rect" size
                maxRect = QtCore.QRect(xpos,
                                       self.height() - 2,
                                       xdim - 2,
                                       2 - self.height())

                # Set QLinearGradient start and final-stop position
                self.grad.setStart(maxRect.topLeft())
                self.grad.setFinalStop(maxRect.bottomRight())

                # Draw peak (audio peak in dB)
                rect = QtCore.QRect(xpos, self.height() - 2, xdim - 2, -peak)
                qp.setOpacity(0.6)
                qp.fillRect(rect, self.grad)
                qp.setOpacity(1.0)

                # Draw rms (in db)
                rect = QtCore.QRect(xpos, self.height() - 2, xdim - 2, -rms)
                qp.fillRect(rect, self.grad)

                # Draw decay peak
                decRect = QtCore.QRect(xpos, (self.height() - 3) - decPeak,
                                       xdim - 2, 2)
                qp.fillRect(decRect, self.grad)

                # Draw Borders
                if self.clipping.get(n, False):
                    qp.setPen(QColor(200, 0, 0))
                else:
                    qp.setPen(QColor(100, 100, 100))

                qp.drawRect(maxRect)

                xpos += xdim

            qp.end()
