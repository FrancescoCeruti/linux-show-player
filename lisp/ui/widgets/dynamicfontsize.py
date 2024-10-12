# This file is part of Linux Show Player
#
# Python adaptation of https://github.com/jonaias/DynamicFontSizeWidgets
#
# Copyright 2019 Francesco Ceruti <ceppofrancy@gmail.com>
#
# Linux Show Player is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Linux Show Player is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Linux Show Player.  If not, see <http://www.gnu.org/licenses/>.

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QFontMetricsF
from PyQt6.QtWidgets import QLabel, QPushButton


class DynamicFontSizeMixin:
    FONT_PRECISION = 0.5
    FONT_PADDING = 8

    def getWidgetMaximumFontSize(self, text: str):
        font = self.font()
        currentSize = font.pointSizeF()

        if not text:
            return currentSize

        widgetRect = QRectF(self.contentsRect())
        widgetWidth = widgetRect.width() - self.FONT_PADDING
        widgetHeight = widgetRect.height() - self.FONT_PADDING

        step = currentSize / 2.0
        # If too small, increase step
        if step <= self.FONT_PRECISION:
            step = self.FONT_PRECISION * 4.0

        lastTestedSize = currentSize
        currentHeight = 0
        currentWidth = 0

        # Check what flags we need to apply
        flags = 0
        if isinstance(self, QLabel):
            flags |= self.alignment()
            flags |= Qt.TextFlag.TextWordWrap if self.wordWrap() else 0

        # Only stop when step is small enough and new size is smaller than QWidget
        while (
            step > self.FONT_PRECISION
            or currentHeight > widgetHeight
            or currentWidth > widgetWidth
        ):
            # Keep last tested value
            lastTestedSize = currentSize
            # Test font size
            font.setPointSizeF(currentSize)
            # Calculate text size
            newFontSizeRect = QFontMetricsF(font).boundingRect(
                widgetRect, flags, text
            )
            currentHeight = newFontSizeRect.height()
            currentWidth = newFontSizeRect.width()

            # If new font size is too big, decrease it
            if currentHeight > widgetHeight or currentWidth > widgetWidth:
                currentSize -= step
                # If step is small enough, keep it ant, so it converge to biggest font size
                if step > self.FONT_PRECISION:
                    step /= 2.0
                # Do not allow negative size
                if currentSize <= 0:
                    break
            else:
                # If new font size is smaller than maximum possible size, increase it
                currentSize += step

        return lastTestedSize


class DynamicFontSizePushButton(DynamicFontSizeMixin, QPushButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def paintEvent(self, event):
        newFont = self.font()
        newFont.setPointSizeF(self.getWidgetMaximumFontSize(self.text()))

        self.setFont(newFont)

        super().paintEvent(event)
