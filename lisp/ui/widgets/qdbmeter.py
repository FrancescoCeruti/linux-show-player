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

from PyQt5 import QtCore
from PyQt5.QtGui import QLinearGradient, QColor, QPainter
from PyQt5.QtWidgets import QWidget

from lisp.core.configuration import config
from lisp.core.decorators import suppress_exceptions


class QDbMeter(QWidget):
    DB_MIN = int(config["DbMeter"]["dbMin"])
    DB_MAX = int(config["DbMeter"]["dbMax"])
    DB_CLIP = int(config["DbMeter"]["dbClip"])

    def __init__(self, parent):
        super().__init__(parent)

        db_range = abs(self.DB_MIN - self.DB_MAX)
        yellow = abs(self.DB_MIN + 20) / db_range  # -20 db
        red = abs(self.DB_MIN) / db_range          # 0 db

        self.grad = QLinearGradient()
        self.grad.setColorAt(0, QColor(0, 255, 0))            # Green
        self.grad.setColorAt(yellow, QColor(255, 255, 0))     # Yellow
        self.grad.setColorAt(red, QColor(255, 0, 0))          # Red

        self.reset()

    def reset(self):
        self.peaks = [self.DB_MIN, self.DB_MIN]
        self.rmss = [self.DB_MIN, self.DB_MIN]
        self.decPeak = [self.DB_MIN, self.DB_MIN]
        self.clipping = {}
        self.repaint()

    def plot(self, peaks, rms, decPeak):
        self.peaks = peaks
        self.rmss = rms
        self.decPeak = decPeak

        self.repaint()

    @suppress_exceptions
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

            dPeaks = []
            for dPeak in self.decPeak:
                if dPeak < self.DB_MIN:
                    dPeak = self.DB_MIN
                elif dPeak > self.DB_MAX:
                    dPeak = self.DB_MAX

                dPeaks.append(round((dPeak - self.DB_MIN) * mul))

            qp = QPainter()
            qp.begin(self)
            qp.setBrush(QColor(0, 0, 0, 0))

            xpos = 0
            xdim = self.width() / len(peaks)

            for n, (peak, rms, dPeak) in enumerate(zip(peaks, rmss, dPeaks)):
                # Maximum "peak-rect" size
                maxRect = QtCore.QRect(xpos, self.height() - 2, xdim - 2,
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
                decRect = QtCore.QRect(xpos, (self.height() - 3) - dPeak,
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
