# This file is part of Linux Show Player
#
# Copyright 2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtWidgets import QMessageBox


class QDetailedMessageBox(QMessageBox):
    """QMessageBox providing statics methods to show detailed-text"""

    @staticmethod
    def dcritical(title, text, detailed_text, parent=None):
        """MessageBox with "Critical" icon"""
        QDetailedMessageBox.dgeneric(
            title, text, detailed_text, QMessageBox.Critical, parent
        )

    @staticmethod
    def dwarning(title, text, detailed_text, parent=None):
        """MessageBox with "Warning" icon"""
        QDetailedMessageBox.dgeneric(
            title, text, detailed_text, QMessageBox.Warning, parent
        )

    @staticmethod
    def dinformation(title, text, detailed_text, parent=None):
        """MessageBox with "Information" icon"""
        QDetailedMessageBox.dgeneric(
            title, text, detailed_text, QMessageBox.Information, parent
        )

    @staticmethod
    def dgeneric(title, text, detail_text, icon, parent=None):
        """Build and show a MessageBox with detailed text"""
        messageBox = QMessageBox(parent)

        messageBox.setIcon(icon)
        messageBox.setWindowTitle(title)
        messageBox.setText(text)
        # Show the detail text only if not an empty string
        if detail_text.strip() != "":
            messageBox.setDetailedText(detail_text)
        messageBox.addButton(QMessageBox.Ok)
        messageBox.setDefaultButton(QMessageBox.Ok)

        messageBox.exec()
