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

import logging
import re
from copy import copy

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, QLineEdit, \
    QTreeWidget, QTreeWidgetItem, QPushButton, QSpacerItem

from lisp.application import Application
from lisp.application import MainActionsHandler
from lisp.modules.rename_cues.rename_action import RenameCueAction
from lisp.ui.ui_utils import translate


class RenameUi(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.__cue_names = []
        self.__cue_names_preview = []
        # Here will be stored regex result in the same order as the cue names above
        self.__cue_names_regex_groups = []

        self.setWindowTitle(translate('RenameCues', 'Rename cues'))
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(650, 350)

        self.setLayout(QGridLayout())

        # Preview List
        self.previewList = QTreeWidget()
        self.previewList.setColumnCount(2)
        self.previewList.setHeaderLabels([
            translate('RenameCues', 'Current'),
            translate('RenameCues', 'Preview')
        ])
        self.previewList.resizeColumnToContents(0)
        self.previewList.resizeColumnToContents(1)
        self.previewList.setColumnWidth(0, 300)
        self.layout().addWidget(self.previewList, 0, 0, 3, 4)

        # Options buttons
        self.capitalizeButton = QPushButton()
        self.capitalizeButton.setText(translate('RenameCues', 'Capitalize'))
        self.capitalizeButton.clicked.connect(self.onCapitalizeButtonClicked)
        self.layout().addWidget(self.capitalizeButton, 3, 0)

        self.lowerButton = QPushButton()
        self.lowerButton.setText(translate('RenameCues', 'Lowercase'))
        self.lowerButton.clicked.connect(self.onLowerButtonClicked)
        self.layout().addWidget(self.lowerButton, 4, 0)

        self.upperButton = QPushButton()
        self.upperButton.setText(translate('RenameCues', 'Uppercase'))
        self.upperButton.clicked.connect(self.onUpperButtonClicked)
        self.layout().addWidget(self.upperButton, 5, 0)

        self.removeNumButton = QPushButton()
        self.removeNumButton.setText(translate('RenameCues', 'Remove Numbers'))
        self.removeNumButton.clicked.connect(self.onRemoveNumButtonClicked)
        self.layout().addWidget(self.removeNumButton, 3, 1)

        self.addNumberingButton = QPushButton()
        self.addNumberingButton.setText(translate('RenameCues', 'Add numbering'))
        self.addNumberingButton.clicked.connect(self.onAddNumberingButtonClicked)
        self.layout().addWidget(self.addNumberingButton, 4, 1)

        self.resetButton = QPushButton()
        self.resetButton.setText(translate('RenameCues', 'Reset'))
        self.resetButton.clicked.connect(self.onResetButtonClicked)
        self.layout().addWidget(self.resetButton, 5, 1)

        # Spacer
        self.layout().addItem(QSpacerItem(30, 0), 3, 2)

        # Regex lines
        self.outRegexLine = QLineEdit()
        self.outRegexLine.setPlaceholderText(
            translate('RenameCues', 'Rename all cue. () in regex below usable with $0, $1 ...'))
        self.outRegexLine.textChanged.connect(self.onOutRegexChanged)
        self.layout().addWidget(self.outRegexLine, 3, 3)

        self.regexLine = QLineEdit()
        self.regexLine.setPlaceholderText(translate('RenameCues', 'Type your regex here :'))
        self.regexLine.textChanged.connect(self.onRegexLineChanged)
        self.layout().addWidget(self.regexLine, 4, 3)

        # OK / Cancel buttons
        self.dialogButtons = QDialogButtonBox()
        self.dialogButtons.setStandardButtons(QDialogButtonBox.Ok |
                                              QDialogButtonBox.Cancel)
        self.layout().addWidget(self.dialogButtons, 6, 3)

        self.dialogButtons.accepted.connect(self.accept)
        self.dialogButtons.rejected.connect(self.reject)

    def get_cues_name(self):
        for cue in Application().layout.get_selected_cues():
            self.__cue_names.append(cue.name)
        self.__cue_names_preview = copy(self.__cue_names)
        # Initialization for regex matches
        self.__cue_names_regex_groups = [() for i in self.__cue_names]

        self.update_preview_list()

    def update_preview_list(self):
        self.previewList.clear()

        if self.__cue_names != []:
            for i, cue in enumerate(self.__cue_names):
                a = QTreeWidgetItem(self.previewList)
                a.setText(0, cue)
                a.setText(1, self.__cue_names_preview[i])

    def onCapitalizeButtonClicked(self):
        self.__cue_names_preview = [
            x.title() for x in self.__cue_names_preview]
        self.update_preview_list()

    def onLowerButtonClicked(self):
        self.__cue_names_preview = [
            x.lower() for x in self.__cue_names_preview]
        self.update_preview_list()

    def onUpperButtonClicked(self):
        self.__cue_names_preview = [
            x.upper() for x in self.__cue_names_preview]
        self.update_preview_list()

    def onRemoveNumButtonClicked(self):
        regex = re.compile('^[^a-zA-Z]+(.+)')

        def remove_numb(input):
            match = regex.search(input)
            if match is not None:
                return match.group(1)
            else:
                return input

        self.__cue_names_preview = [
            remove_numb(x) for x in self.__cue_names_preview]

        self.update_preview_list()

    def onAddNumberingButtonClicked(self):
        cues_nbr = len(self.__cue_names)
        digit_nbr = len(str(cues_nbr))
        self.__cue_names_preview = [
            f"{i+1:0{digit_nbr}.0f} - {cue_name}"
            for i, cue_name in enumerate(self.__cue_names_preview)
        ]

        self.update_preview_list()

    def onResetButtonClicked(self):
        self.__cue_names_preview = copy(self.__cue_names)

        self.update_preview_list()

    def onRegexLineChanged(self):
        pattern = self.regexLine.text()
        try:
            regex = re.compile(pattern)
        except re.error:
            logging.info("Regex error : not a valid pattern")
        else:
            for i, cue_name in enumerate(self.__cue_names):
                result = regex.search(cue_name)
                if result:
                    self.__cue_names_regex_groups[i] = result.groups()

            self.onOutRegexChanged()

    def onOutRegexChanged(self):
        out_pattern = self.outRegexLine.text()

        if out_pattern == '':
            self.__cue_names_preview = copy(self.__cue_names)
        else:
            for i, cue_name in enumerate(self.__cue_names):
                out_string = out_pattern
                for n in range(len(self.__cue_names_regex_groups[0])):
                    pattern = '\${}'.format(n)
                    try:
                        out_string = re.sub(pattern,
                                            self.__cue_names_regex_groups[i][n], out_string)
                    except IndexError:
                        logging.info("Regex error : Catch with () before display with $n")
                self.__cue_names_preview[i] = out_string

        self.update_preview_list()

    def record_cues_name(self):
        MainActionsHandler.do_action(
            RenameCueAction(self.__cue_names_preview)
        )

if __name__ == "__main__":
    # To test Ui quickly
    from PyQt5.QtWidgets import QApplication
    import sys

    gui_test_app = QApplication(sys.argv)
    rename_ui = RenameUi()
    rename_ui.show()
    sys.exit(gui_test_app.exec())
