# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2016-2017 Aurelien Cibrario <aurelien.cibrario@gmail.com>
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

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, QLineEdit, \
    QTreeWidget, QAbstractItemView, QTreeWidgetItem, QPushButton, QSpacerItem, \
    QMessageBox

from lisp.application import MainActionsHandler
from lisp.modules.rename_cues.rename_action import RenameCueAction
from lisp.ui.ui_utils import translate


class RenameUi(QDialog):
    def __init__(self, parent=None, selected_cues=[]):
        super().__init__(parent)

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
        self.previewList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.previewList.itemSelectionChanged.connect(self.onPreviewListItemSelectionChanged)
        self.layout().addWidget(self.previewList, 0, 0, 3, 5)

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

        # Help button
        self.helpButton = QPushButton()
        self.helpButton.setIcon(QIcon.fromTheme('help-info'))
        self.helpButton.setIconSize(QSize(32, 32))
        self.layout().addWidget(self.helpButton, 3, 4, 2, 1)
        self.helpButton.clicked.connect(self.onHelpButtonClicked)

        # OK / Cancel buttons
        self.dialogButtons = QDialogButtonBox()
        self.dialogButtons.setStandardButtons(QDialogButtonBox.Ok |
                                              QDialogButtonBox.Cancel)
        self.layout().addWidget(self.dialogButtons, 6, 3)

        self.dialogButtons.accepted.connect(self.accept)
        self.dialogButtons.rejected.connect(self.reject)


        # This list store infos on cues with dicts
        self._cues_list = []
        for cue in selected_cues:
            self._cues_list.append({
                'cue_name': cue.name,
                'cue_preview': cue.name,
                'selected': True,
                'regex_groups': [],
                'id': cue.id
            })

        # Populate Preview list
        for cue_to_rename in self._cues_list:
            item = QTreeWidgetItem(self.previewList)
            item.setText(0, cue_to_rename['cue_name'])
            item.setText(1, cue_to_rename['cue_preview'])
        self.previewList.selectAll()

    def update_preview_list(self):
        for i in range(self.previewList.topLevelItemCount()):
            item = self.previewList.topLevelItem(i)
            item.setText(1, self._cues_list[i]['cue_preview'])

    def onPreviewListItemSelectionChanged(self):
        for i in range(self.previewList.topLevelItemCount()):
            item = self.previewList.topLevelItem(i)
            if item.isSelected():
                self._cues_list[i]['selected'] = True
            else:
                self._cues_list[i]['selected'] = False

    def onCapitalizeButtonClicked(self):
        for cue in self._cues_list:
            if cue['selected']:
                cue['cue_preview'] = cue['cue_preview'].title()
        self.update_preview_list()

    def onLowerButtonClicked(self):
        for cue in self._cues_list:
            if cue['selected']:
                cue['cue_preview'] = cue['cue_preview'].lower()
        self.update_preview_list()

    def onUpperButtonClicked(self):
        for cue in self._cues_list:
            if cue['selected']:
                cue['cue_preview'] = cue['cue_preview'].upper()
        self.update_preview_list()

    def onRemoveNumButtonClicked(self):
        regex = re.compile('^[^a-zA-Z]+(.+)')

        for cue in self._cues_list:
            if cue['selected']:
                match = regex.search(cue['cue_preview'])
                if match is not None:
                    cue['cue_preview'] = match.group(1)

        self.update_preview_list()

    def onAddNumberingButtonClicked(self):
        # Extract selected rows
        cues_to_modify = [cue for cue in self._cues_list if cue['selected']]
        # Count selected rows
        cues_nbr = len(cues_to_modify)
        # Calculate number of digits in order to add appropriate number of 0's
        digit_nbr = len(str(cues_nbr))

        for i, cue in enumerate(cues_to_modify):
            if cue['selected']:
                cue['cue_preview'] = f"{i+1:0{digit_nbr}.0f} - {cue['cue_preview']}"

        self.update_preview_list()

    def onResetButtonClicked(self):
        for cue in self._cues_list:
            cue['cue_preview'] = cue['cue_name']
            cue['selected'] = True

        self.update_preview_list()
        self.previewList.selectAll()

    def onHelpButtonClicked(self):

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(translate('RenameCues', 'Regex help'))
        msg.setText(translate('RenameCues',
                              "You can use Regexes to rename your cues.\n\n"
                              "Insert expressions captured with regexes in the "
                              "line below with $0 for the first parenthesis, $1 for"
                              "the second, etc...\n"
                              "In the second line, you can use standard Python Regexes "
                              "to match expressions in the original cues names. Use "
                              "parenthesis to capture parts of the matched expression.\n\n"
                              "Exemple : \n^[a-z]([0-9]+) will find a lower case character ([a-z]), "
                              "followed by one or more number.\n"
                              "Only the numbers are between parenthesis and will be usable with "
                              "$0 in the first line.\n\n"
                              "For more information about Regexes, consult python documentation"))
        msg.exec_()

    def onRegexLineChanged(self):
        pattern = self.regexLine.text()
        try:
            regex = re.compile(pattern)
        except re.error:
            logging.debug("Regex error : not a valid pattern")
        else:
            for cue in self._cues_list:
                result = regex.search(cue['cue_name'])
                if result:
                    cue['regex_groups'] = result.groups()

            self.onOutRegexChanged()

    def onOutRegexChanged(self):
        out_pattern = self.outRegexLine.text()

        if out_pattern == '':
            for cue in self._cues_list:
                if cue['selected']:
                    cue['cue_preview'] = cue['cue_name']
        else:
            for cue in self._cues_list:
                out_string = out_pattern
                for n in range(len(cue['regex_groups'])):
                    pattern = f"\${n}"
                    try:
                        out_string = re.sub(pattern,
                                            cue['regex_groups'][n], out_string)
                    except IndexError:
                        logging.debug("Regex error : Catch with () before display with $n")
                if cue['selected']:
                    cue['cue_preview'] = out_string

        self.update_preview_list()

    def record_cues_name(self):
        MainActionsHandler.do_action(
            RenameCueAction(self._cues_list)
        )

if __name__ == "__main__":
    # To test Ui quickly
    from PyQt5.QtWidgets import QApplication
    import sys

    # Put a few names for test
    class FakeCue:
        def __init__(self, name, id):
            self.name = name
            self.id = id

    cue1 = FakeCue('Cue Name',        '3829434920')
    cue2 = FakeCue('Other Name',      '4934893213')
    cue3 = FakeCue('Foo Bar foo bar', '4985943859')
    cue4 = FakeCue('blablablabla',    '9938492384')

    fake_cue_list = [cue1, cue2, cue3, cue4]

    gui_test_app = QApplication(sys.argv)
    rename_ui = RenameUi(None, fake_cue_list)


    rename_ui.show()

    sys.exit(gui_test_app.exec())
