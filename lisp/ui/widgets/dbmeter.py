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

from math import ceil
from typing import Callable

from PyQt5.QtCore import QPointF, QRect, QRectF, Qt, QPoint
from PyQt5.QtGui import (
    QLinearGradient,
    QColor,
    QPainter,
    QPixmap,
    QFontDatabase,
    QFontMetrics,
)
from PyQt5.QtWidgets import QWidget

from lisp.backend.audio_utils import iec_scale


class DBMeter(QWidget):
    """DPM - Digital Peak Meter widget"""

    scale_steps = [1, 5, 10, 20, 50]

    def __init__(
        self,
        parent=None,
        dBMin: int = -70,
        dBMax: int = 0,
        clipping: int = 0,
        smoothing: float = 0.66,
        scale: Callable = iec_scale,
        unit: str = "dBFS",
        **kwargs,
    ):
        super().__init__(parent, **kwargs)
        self.dBMin = dBMin
        self.dBMax = dBMax
        self.dbClipping = clipping
        self.valueSmoothing = smoothing
        self.scale = scale
        self.unit = unit

        self.backgroundColor = QColor(32, 32, 32)
        self.borderColor = QColor(80, 80, 80)
        self.clippingColor = QColor(220, 50, 50)

        self._currentSmoothing = self.valueSmoothing
        self._markings = []
        self._pixmap = QPixmap()
        self._scale_width = 0
        self._paint_scale_text = True

        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(font.pointSize() - 3)
        self.setFont(font)
        font.setPointSize(font.pointSize() - 1)
        self.unit_font = font

        self.reset()

    def reset(self):
        self.peaks = [self.dBMin, self.dBMin]
        self.decayPeaks = [self.dBMin, self.dBMin]
        self.clipping = {}

        self.update()

    def plot(self, peaks, _, decayPeak):
        for n in range(min(len(peaks), len(self.peaks))):
            if peaks[n] > self.dbClipping:
                self.clipping[n] = True

            if self.valueSmoothing:
                if peaks[n] < self.peaks[n]:
                    peaks[n] = self.peaks[n] - self._currentSmoothing
                    self._currentSmoothing *= 1.1
                else:
                    self._currentSmoothing = self.valueSmoothing

        self.peaks = peaks
        self.decayPeaks = decayPeak

        # Update, excluding the scale labels
        self.update(0, 0, self.width() - self._scale_width, self.height())

    def updateMarkings(self):
        self._markings = []

        fm = QFontMetrics(self.font())
        height = self.height()
        # We assume that we're using numerals that lack descenders
        font_height = fm.ascent()
        curr_level = self.dBMax
        curr_y = ceil(font_height / 2)

        while curr_y < height - font_height:
            prev_level = curr_level
            prev_y = curr_y + font_height

            for step in self.scale_steps:
                curr_level = prev_level - step
                curr_y = height - self.scale(curr_level) * (height - 2)
                if curr_y > prev_y:
                    break

            self._markings.append([curr_y, curr_level])

        self._markings.pop()

        self._scale_width = (
            max(
                fm.boundingRect(str(self.dBMin)).width(),
                fm.boundingRect(str(self.dBMax)).width(),
                QFontMetrics(self.unit_font).boundingRect(self.unit).width(),
            )
            + 2
        )

        # Decide if the widget is too small to draw the scale labels
        if self.width() <= self._scale_width * 2:
            self._scale_width = 0

    def updatePixmap(self):
        """Prepare the colored rect to be used during paintEvent(s)"""
        w = self.width()
        h = self.height()

        dbRange = abs(self.dBMin - self.dBMax)

        gradient = QLinearGradient(0, 0, 0, h)
        gradient.setColorAt(0, QColor(230, 0, 0))
        gradient.setColorAt(10 / dbRange, QColor(255, 220, 0))
        gradient.setColorAt(30 / dbRange, QColor(0, 220, 0))
        gradient.setColorAt(1, QColor(0, 160, 0))

        self._pixmap = QPixmap(w, h)
        QPainter(self._pixmap).fillRect(0, 0, w, h, gradient)

    def resizeEvent(self, event):
        self.updatePixmap()
        self.updateMarkings()

    def paintEvent(self, event):
        height = self.height()
        width = self.width()

        painter = QPainter()
        painter.begin(self)
        painter.setBrush(self.backgroundColor)

        # Calculate the meter size (per single channel)
        usableWidth = width - self._scale_width
        meterWidth = usableWidth / len(self.peaks)
        meterRect = QRectF(0, 0, meterWidth - 2, height - 1)

        # Draw each channel
        for n, values in enumerate(zip(self.peaks, self.decayPeaks)):
            # Draw Background
            if self.clipping.get(n, False):
                painter.setPen(self.clippingColor)
            else:
                painter.setPen(self.borderColor)

            painter.drawRect(meterRect)

            # Limit the values between dbMin and dbMax
            peak = max(self.dBMin, min(self.dBMax, values[0]))
            decayPeak = max(self.dBMin, min(self.dBMax, values[1]))
            # Scale the values to the widget height
            peak = self.scale(peak) * (height - 2)
            decayPeak = self.scale(decayPeak) * (height - 2)

            # Draw peak (audio peak in dB)
            peakRect = QRectF(
                meterRect.x() + 1,
                height - peak - 1,
                meterRect.width() - 1,
                peak,
            )
            painter.drawPixmap(peakRect, self._pixmap, peakRect)

            # Draw decay indicator
            decayRect = QRectF(
                meterRect.x() + 1,
                height - decayPeak - 1,
                meterRect.width() - 1,
                1,
            )
            painter.drawPixmap(decayRect, self._pixmap, decayRect)

            # Draw markings
            x_start = meterRect.x() + meterRect.width() / 2
            x_end = meterRect.x() + meterRect.width()
            for mark in self._markings:
                painter.drawLine(
                    QPointF(x_start, mark[0]), QPointF(x_end, mark[0])
                )

            # Move to the next meter
            meterRect.translate(meterWidth, 0)

        if self._scale_width > 0 and event.region().contains(
            QPoint(usableWidth, 0)
        ):
            # Draw the scale marking text
            text_height = QFontMetrics(self.font()).height()
            text_offset = text_height / 2
            painter.setPen(self.palette().windowText().color())
            painter.drawText(
                QRectF(0, 0, width, text_height), Qt.AlignRight, str(self.dBMax)
            )
            for mark in self._markings:
                painter.drawText(
                    QRectF(0, mark[0] - text_offset, width, width),
                    Qt.AlignRight,
                    str(mark[1]),
                )

            # Draw the units that the scale uses
            text_height = QFontMetrics(self.unit_font).height()
            painter.setFont(self.unit_font)
            painter.drawText(
                QRectF(0, height - text_height, width, text_height),
                Qt.AlignRight,
                self.unit,
            )

            painter.end()
