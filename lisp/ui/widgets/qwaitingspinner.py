"""
The MIT License (MIT)

Copyright (c) 2012-2014 Alexander Turkin
Copyright (c) 2014 William Hallatt
Copyright (c) 2015 Jacob Dawid
Copyright (c) 2016 Luca Weiss
Copyright (c) 2020 Francesco Ceruti

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import math

from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QWidget


class QWaitingSpinner(QWidget):
    def __init__(
        self,
        parent=None,
        centerOnParent=Qt.AlignmentFlag.AlignCenter,
        disableParentWhenSpinning=False,
        modality=Qt.WindowModality.NonModal,
    ):
        super().__init__(parent)
        self.setWindowModality(modality)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._centerOnParent = centerOnParent
        self._disableParentWhenSpinning = disableParentWhenSpinning

        self._color = Qt.GlobalColor.gray
        self._roundness = 100.0
        self._minimumTrailOpacity = math.pi
        self._trailFadePercentage = 80.0
        self._revolutionsPerSecond = math.pi / 2
        self._numberOfLines = 10
        self._lineLength = 5
        self._lineWidth = 5
        self._innerRadius = 10
        self._currentCounter = 0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.rotate)

        self.updateSize()
        self.updateTimer()
        self.hide()

    def paintEvent(self, QPaintEvent):
        self.updatePosition()
        linesRect = QRectF(
            0, -self._lineWidth / 2, self._lineLength, self._lineWidth
        )

        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.translate(
            self._innerRadius + self._lineLength,
            self._innerRadius + self._lineLength,
        )

        for i in range(self._numberOfLines):
            rotateAngle = i / self._numberOfLines * 360
            distance = self.lineCountDistanceFromPrimary(
                i, self._currentCounter, self._numberOfLines
            )
            color = self.currentLineColor(
                distance,
                self._numberOfLines,
                self._trailFadePercentage,
                self._minimumTrailOpacity,
                self._color,
            )

            painter.save()
            painter.rotate(rotateAngle)
            painter.translate(self._innerRadius, 0)
            painter.setBrush(color)
            painter.drawRoundedRect(
                linesRect,
                self._roundness,
                self._roundness,
                Qt.SizeMode.RelativeSize,
            )
            painter.restore()

    def start(self):
        self.updatePosition()
        self.show()

        if self.parentWidget and self._disableParentWhenSpinning:
            self.parentWidget().setEnabled(False)

        if not self._timer.isActive():
            self._timer.start()
            self._currentCounter = 0

    def stop(self):
        self.hide()

        if self.parentWidget() and self._disableParentWhenSpinning:
            self.parentWidget().setEnabled(True)

        if self._timer.isActive():
            self._timer.stop()
            self._currentCounter = 0

    def setNumberOfLines(self, lines):
        self._numberOfLines = lines
        self._currentCounter = 0
        self.updateTimer()

    def setLineLength(self, length):
        self._lineLength = length
        self.updateSize()

    def setLineWidth(self, width):
        self._lineWidth = width
        self.updateSize()

    def setInnerRadius(self, radius):
        self._innerRadius = radius
        self.updateSize()

    def color(self):
        return self._color

    def roundness(self):
        return self._roundness

    def minimumTrailOpacity(self):
        return self._minimumTrailOpacity

    def trailFadePercentage(self):
        return self._trailFadePercentage

    def revolutionsPersSecond(self):
        return self._revolutionsPerSecond

    def numberOfLines(self):
        return self._numberOfLines

    def lineLength(self):
        return self._lineLength

    def lineWidth(self):
        return self._lineWidth

    def innerRadius(self):
        return self._innerRadius

    def isSpinning(self):
        return self._timer.isActive()

    def setRoundness(self, roundness):
        self._roundness = max(0.0, min(100.0, roundness))

    def setColor(self, color=Qt.GlobalColor.gray):
        self._color = QColor(color)

    def setRevolutionsPerSecond(self, revolutionsPerSecond):
        self._revolutionsPerSecond = revolutionsPerSecond
        self.updateTimer()

    def setTrailFadePercentage(self, trail):
        self._trailFadePercentage = trail

    def setMinimumTrailOpacity(self, minimumTrailOpacity):
        self._minimumTrailOpacity = minimumTrailOpacity

    def rotate(self):
        self._currentCounter += 1
        if self._currentCounter >= self._numberOfLines:
            self._currentCounter = 0

        self.update()

    def updateSize(self):
        size = (self._innerRadius + self._lineLength) * 2
        self.setFixedSize(size, size)

    def updateTimer(self):
        self._timer.setInterval(
            int(1000 / (self._numberOfLines * self._revolutionsPerSecond))
        )

    def updatePosition(self):
        if self.parentWidget() and self._centerOnParent:
            x = self.x()
            y = self.y()

            if self._centerOnParent & Qt.AlignmentFlag.AlignHCenter:
                x = int(self.parentWidget().width() / 2 - self.width() / 2)
            if self._centerOnParent & Qt.AlignmentFlag.AlignVCenter:
                y = int(self.parentWidget().height() / 2 - self.height() / 2)

            self.move(x, y)

    def lineCountDistanceFromPrimary(self, current, primary, totalNrOfLines):
        distance = primary - current
        if distance < 0:
            distance += totalNrOfLines

        return distance

    def currentLineColor(
        self,
        countDistance,
        totalNrOfLines,
        trailFadePerc,
        minOpacity,
        colorInput,
    ):
        if countDistance == 0:
            return colorInput

        color = QColor(colorInput)
        minAlphaF = minOpacity / 100.0
        distanceThreshold = math.ceil(
            (totalNrOfLines - 1) * trailFadePerc / 100.0
        )

        if countDistance > distanceThreshold:
            color.setAlphaF(minAlphaF)
        else:
            alphaDiff = color.alphaF() - minAlphaF
            gradient = alphaDiff / (distanceThreshold + 1)
            resultAlpha = color.alphaF() - gradient * countDistance
            # If alpha is out of bounds, clip it.
            resultAlpha = min(1.0, max(0.0, resultAlpha))
            color.setAlphaF(resultAlpha)

        return color
