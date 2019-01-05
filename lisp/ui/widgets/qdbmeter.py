# This file is part of Linux Show Player
#
# Copyright 2018 Francesco Ceruti <ceppofrancy@gmail.com>
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


class QDbMeter(QWidget):
    def __init__(self, parent, min=-60, max=0, clip=0):
        super().__init__(parent)
        self.db_min = min
        self.db_max = max
        self.db_clip = clip

        db_range = abs(self.db_min - self.db_max)
        yellow = abs(self.db_min + 20) / db_range  # -20 db
        red = abs(self.db_min) / db_range  # 0 db

        self.grad = QLinearGradient()
        self.grad.setColorAt(0, QColor(0, 255, 0))  # Green
        self.grad.setColorAt(yellow, QColor(255, 255, 0))  # Yellow
        self.grad.setColorAt(red, QColor(255, 0, 0))  # Red

        self.reset()

    def reset(self):
        self.peaks = [self.db_min, self.db_min]
        self.rmss = [self.db_min, self.db_min]
        self.decPeak = [self.db_min, self.db_min]
        self.clipping = {}
        self.repaint()

    def plot(self, peaks, rms, decPeak):
        self.peaks = peaks
        self.rmss = rms
        self.decPeak = decPeak

        self.repaint()

    def paintEvent(self, e):
        if not self.visibleRegion().isEmpty():
            # Stretch factor
            mul = self.height() - 4
            mul /= self.db_max - self.db_min

            peaks = []
            for n, peak in enumerate(self.peaks):
                if peak > self.db_clip:
                    self.clipping[n] = True

                # Checks also for NaN values
                if peak < self.db_min or peak != peak:
                    peak = self.db_min
                elif peak > self.db_max:
                    peak = self.db_max

                peaks.append(round((peak - self.db_min) * mul))

            rmss = []
            for rms in self.rmss:
                # Checks also for NaN values
                if rms < self.db_min or rms != rms:
                    rms = self.db_min
                elif rms > self.db_max:
                    rms = self.db_max

                rmss.append(round((rms - self.db_min) * mul))

            dPeaks = []
            for dPeak in self.decPeak:
                # Checks also for NaN values
                if dPeak < self.db_min or dPeak != dPeak:
                    dPeak = self.db_min
                elif dPeak > self.db_max:
                    dPeak = self.db_max

                dPeaks.append(round((dPeak - self.db_min) * mul))

            qp = QPainter()
            qp.begin(self)
            qp.setBrush(QColor(0, 0, 0, 0))

            xpos = 0
            xdim = self.width() / len(peaks)

            for n, (peak, rms, dPeak) in enumerate(zip(peaks, rmss, dPeaks)):
                # Maximum 'peak-rect' size
                maxRect = QtCore.QRect(
                    xpos, self.height() - 2, xdim - 2, 2 - self.height()
                )

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
                decRect = QtCore.QRect(
                    xpos, (self.height() - 3) - dPeak, xdim - 2, 2
                )
                qp.fillRect(decRect, self.grad)

                # Draw Borders
                if self.clipping.get(n, False):
                    qp.setPen(QColor(200, 0, 0))
                else:
                    qp.setPen(QColor(100, 100, 100))

                qp.drawRect(maxRect)

                xpos += xdim

            qp.end()
