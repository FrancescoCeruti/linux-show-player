from math import floor, ceil

from PyQt5.QtCore import QLineF, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush
from PyQt5.QtWidgets import QWidget

from lisp.core.signal import Connection


class WaveformWidget(QWidget):
    def __init__(self, waveform, **kwargs):
        super().__init__(**kwargs)
        self._waveform = waveform
        self._maximum = self._waveform.duration
        self._valueToPx = 0
        self._value = 0
        self._lastDrawnValue = 0

        self.elapsedPeakColor = QColor(75, 154, 250)
        self.elapsedRmsColor = QColor(153, 199, 255)
        self.remainsPeakColor = QColor(90, 90, 90)
        self.remainsRmsColor = QColor(130, 130, 130)

        # Watch for the waveform to be ready
        self._waveform.ready.connect(self._ready, Connection.QtQueued)
        # Load the waveform
        self._waveform.load_waveform()

    def _ready(self):
        self.setMaximum(self._waveform.duration)
        self.update()

    def maximum(self):
        return self._maximum

    def setMaximum(self, maximum):
        self._maximum = maximum
        self._valueToPx = self._maximum / self.width()
        self.update()

    def value(self):
        return self._value

    def setValue(self, value):
        self._value = min(value, self._maximum)

        if self.isVisible():
            # Repaint only if we have new pixels to draw
            if self._value >= floor(self._lastDrawnValue + self._valueToPx):
                x = self._lastDrawnValue / self._valueToPx
                width = (self._value - self._lastDrawnValue) / self._valueToPx
                # Repaint only the changed area
                self.update(floor(x), 0, ceil(width), self.height())
            elif self._value <= ceil(self._lastDrawnValue - self._valueToPx):
                x = self._value / self._valueToPx
                width = (self._lastDrawnValue - self._value) / self._valueToPx
                # Repaint only the changed area
                self.update(floor(x), 0, ceil(width) + 1, self.height())

    def resizeEvent(self, event):
        self._valueToPx = self._maximum / self.width()

    def paintEvent(self, event):
        halfHeight = self.height() / 2

        painter = QPainter()
        painter.begin(self)

        pen = QPen()
        pen.setWidth(1)
        painter.setPen(pen)

        if self._valueToPx and self._waveform.is_ready():
            peakSamples = self._waveform.peak_samples
            rmsSamples = self._waveform.rms_samples
            samplesToPx = len(peakSamples) / self.width()
            elapsedWidth = floor(self._value / self._valueToPx)

            peakElapsedLines = []
            peakRemainsLines = []
            rmsElapsedLines = []
            rmsRemainsLines = []
            for x in range(event.rect().x(), self.rect().right()):
                # Calculate re-sample interval
                s0 = floor(x * samplesToPx)
                s1 = ceil(x * samplesToPx + samplesToPx)
                # Re-sample the values
                peak = max(peakSamples[s0:s1]) * halfHeight
                rms = (sum(rmsSamples[s0:s1]) / samplesToPx) * halfHeight

                # Create lines to draw
                peakLine = QLineF(x, halfHeight + peak, x, halfHeight - peak)
                rmsLine = QLineF(x, halfHeight + rms, x, halfHeight - rms)

                # Decide if elapsed or remaining
                if x <= elapsedWidth:
                    peakElapsedLines.append(peakLine)
                    rmsElapsedLines.append(rmsLine)
                else:
                    peakRemainsLines.append(peakLine)
                    rmsRemainsLines.append(rmsLine)

            # Draw peak for elapsed
            if peakElapsedLines:
                pen.setColor(self.elapsedPeakColor)
                painter.setPen(pen)
                painter.drawLines(peakElapsedLines)

            # Draw rms for elapsed
            if rmsElapsedLines:
                pen.setColor(self.elapsedRmsColor)
                painter.setPen(pen)
                painter.drawLines(rmsElapsedLines)

            # Draw peak for remaining
            if peakRemainsLines:
                pen.setColor(self.remainsPeakColor)
                painter.setPen(pen)
                painter.drawLines(peakRemainsLines)

            # Draw rms for remaining
            if rmsRemainsLines:
                pen.setColor(self.remainsRmsColor)
                painter.setPen(pen)
                painter.drawLines(rmsRemainsLines)

            # Remember the last drawn item
            self._lastDrawnValue = self._value
        else:
            # Draw a single line in the middle
            pen.setColor(self.remainsRmsColor)
            painter.setPen(pen)
            painter.drawLine(0, halfHeight, self.width(), halfHeight)

        painter.end()


class WaveformSlider(WaveformWidget):
    """ Implement an API similar to a QAbstractSlider. """

    sliderMoved = pyqtSignal(int)
    sliderJumped = pyqtSignal(int)

    def __init__(self, waveform, **kwargs):
        super().__init__(waveform, **kwargs)
        self.setMouseTracking(True)

        self._mouseDown = False
        self._lastPosition = -1

        self.backgroundColor = QColor(32, 32, 32)
        self.seekIndicatorColor = QColor(255, 0, 0)

    def leaveEvent(self, event):
        self._lastPosition = -1

    def mouseMoveEvent(self, event):
        self._lastPosition = event.x()
        self.update()

        if self._mouseDown:
            self.sliderMoved.emit(round(self._lastPosition * self._valueToPx))

    def mousePressEvent(self, event):
        self._mouseDown = True

    def mouseReleaseEvent(self, event):
        self._mouseDown = False
        self.sliderJumped.emit(round(event.x() * self._valueToPx))

    def paintEvent(self, event):
        # Draw background
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(QColor(0, 0, 0, 0))
        painter.setPen(pen)
        painter.setBrush(QBrush(self.backgroundColor))
        painter.drawRoundedRect(self.rect(), 6, 6)

        painter.end()

        # Draw the waveform
        super().paintEvent(event)

        # If necessary (mouse-over) draw the seek indicator
        if self._lastPosition >= 0:
            painter.begin(self)

            pen.setWidth(1)
            pen.setColor(self.seekIndicatorColor)
            painter.setPen(pen)

            painter.drawLine(
                self._lastPosition, 0, self._lastPosition, self.height()
            )

            painter.end()
