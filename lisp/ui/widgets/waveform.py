from math import floor, ceil

from PyQt6.QtCore import QLineF, pyqtSignal, Qt, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush
from PyQt6.QtWidgets import QWidget

from lisp.backend.waveform import Waveform
from lisp.core.signal import Connection
from lisp.core.util import strtime
from lisp.ui.widgets.dynamicfontsize import DynamicFontSizeMixin


class WaveformWidget(QWidget):
    def __init__(self, waveform: Waveform, **kwargs):
        super().__init__(**kwargs)
        self._waveform = waveform
        self._maximum = self._waveform.duration
        self._valueToPx = 0
        self._value = 0
        self._lastDrawnValue = 0

        self.backgroundColor = QColor(32, 32, 32)
        self.backgroundRadius = 6
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

        # if we are not visible we can skip this
        if not self.visibleRegion().isEmpty():
            # Repaint only if we have new pixels to draw
            if self._value >= floor(self._lastDrawnValue + self._valueToPx):
                x = int(self._lastDrawnValue / self._valueToPx)
                width = int(
                    (self._value - self._lastDrawnValue) / self._valueToPx
                )
                # Repaint only the changed area
                self.update(x - 1, 0, width + 1, self.height())
            elif self._value <= ceil(self._lastDrawnValue - self._valueToPx):
                x = int(self._value / self._valueToPx)
                width = int(
                    (self._lastDrawnValue - self._value) / self._valueToPx
                )
                # Repaint only the changed area
                self.update(x - 1, 0, width + 2, self.height())

    def resizeEvent(self, event):
        self._valueToPx = self._maximum / self.width()

    def paintEvent(self, event):
        halfHeight = self.height() / 2
        painter = QPainter()
        painter.begin(self)

        # Draw the background (it will be clipped to event.rect())
        pen = QPen(QColor(0, 0, 0, 0))
        painter.setPen(pen)
        painter.setBrush(QBrush(self.backgroundColor))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawRoundedRect(self.rect(), 6, 6)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        # Draw the weveform
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
            for x in range(event.rect().x(), event.rect().right() + 1):
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
                if x < elapsedWidth:
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
            painter.drawLine(QLineF(0, halfHeight, self.width(), halfHeight))

        painter.end()


class WaveformSlider(DynamicFontSizeMixin, WaveformWidget):
    """Implement an API similar to a QAbstractSlider."""

    FONT_PADDING = 1

    sliderMoved = pyqtSignal(int)
    sliderJumped = pyqtSignal(int)

    def __init__(self, waveform, **kwargs):
        super().__init__(waveform, **kwargs)
        self.setMouseTracking(True)

        self._lastPosition = -1
        self._mouseDown = False
        self._labelRight = True
        self._maxFontSize = self.font().pointSizeF()

        self.seekIndicatorColor = QColor(Qt.GlobalColor.red)
        self.seekTimestampBG = QColor(32, 32, 32)
        self.seekTimestampFG = QColor(Qt.GlobalColor.white)

    def _xToValue(self, x):
        return round(x * self._valueToPx)

    def leaveEvent(self, event):
        self._labelRight = True
        self._lastPosition = -1

    def mouseMoveEvent(self, event):
        self._lastPosition = event.x()
        self.update()

        if self._mouseDown:
            self.sliderMoved.emit(self._xToValue(self._lastPosition))

    def mousePressEvent(self, event):
        self._mouseDown = True

    def mouseReleaseEvent(self, event):
        self._mouseDown = False
        self.sliderJumped.emit(self._xToValue(event.x()))

    def resizeEvent(self, event):
        fontSize = self.getWidgetMaximumFontSize("0123456789")
        if fontSize > self._maxFontSize:
            fontSize = self._maxFontSize

        font = self.font()
        font.setPointSizeF(fontSize)
        self.setFont(font)

        super().resizeEvent(event)

    def paintEvent(self, event):
        # Draw the waveform
        super().paintEvent(event)

        # If needed (mouse-over) draw the seek indicator, and it's timestamp
        if self._lastPosition >= 0:
            painter = QPainter()
            painter.begin(self)

            # Draw the indicator as a 1px vertical line
            pen = QPen()
            pen.setWidth(1)
            pen.setColor(self.seekIndicatorColor)
            painter.setPen(pen)
            painter.drawLine(
                self._lastPosition, 0, self._lastPosition, self.height()
            )

            # Get the timestamp of the indicator position
            text = strtime(self._xToValue(self._lastPosition))[:-3]
            textSize = self.fontMetrics().size(Qt.TextFlag.TextSingleLine, text)
            # Vertical offset to center the label
            vOffset = (self.height() - textSize.height()) / 2

            # Decide on which side of the indicator the label should be drawn
            left = self._lastPosition - textSize.width() - 14
            right = self._lastPosition + textSize.width() + 14
            if (self._labelRight and right < self.width()) or left < 0:
                xOffset = self._lastPosition + 6
                self._labelRight = True
            else:
                xOffset = self._lastPosition - textSize.width() - 14
                self._labelRight = False

            # Define the label rect, add 8px of width for left/right padding
            rect = QRectF(
                xOffset, vOffset, textSize.width() + 8, textSize.height()
            )

            # Draw the label rect
            pen.setColor(self.seekIndicatorColor.darker(150))
            painter.setPen(pen)
            painter.setBrush(QBrush(self.seekTimestampBG))
            painter.drawRoundedRect(rect, 2, 2)

            # Draw the timestamp
            pen.setColor(self.seekTimestampFG)
            painter.setPen(pen)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

            painter.end()
