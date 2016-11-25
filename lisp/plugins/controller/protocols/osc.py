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

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
<<<<<<< HEAD
from PyQt5.QtWidgets import QGroupBox, QPushButton, QVBoxLayout, \
    QTableView, QTableWidget, QHeaderView, QGridLayout, QLabel, \
    QDialog, QDialogButtonBox

from lisp.modules import check_module
=======
from PyQt5.QtWidgets import QGroupBox, QPushButton, QComboBox, QVBoxLayout, \
    QMessageBox, QTableView, QTableWidget, QHeaderView, QGridLayout, QLabel, \
    QDialog, QDialogButtonBox

from lisp.modules import check_module
from lisp.application import MainWindow
>>>>>>> 6f32977... implemented OSC Protocol
from lisp.modules.osc.osc_common import OscCommon
from lisp.plugins.controller.protocols.protocol import Protocol
from lisp.ui.qdelegates import ComboBoxDelegate, LineEditDelegate
from lisp.ui.qmodels import SimpleTableModel
from lisp.ui.settings.settings_page import CueSettingsPage
from lisp.ui.ui_utils import translate


class Osc(Protocol):
    def __init__(self):
        super().__init__()

        if check_module('osc') and OscCommon().listening:
            OscCommon().new_message.connect(self.__new_message)

    def __new_message(self, path, args, types, src):
        self.protocol_event.emit(Osc.key_from_message(path, types))

    @staticmethod
    def key_from_message(path, types):
        if len(types):
            return '{0} {1}'.format(path, types)
        else:
            return path

    @staticmethod
    def from_key(message_str):
        m = message_str.split(' ')
        return m[0], '' if len(m) < 2 else m[1]


class OscSettings(CueSettingsPage):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'OSC Controls')

    def __init__(self, cue_class, **kwargs):
        super().__init__(cue_class, **kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.oscGroup = QGroupBox(self)
        self.oscGroup.setTitle(translate('ControllerOscSettings', 'OSC'))
        self.oscGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.oscGroup)

        self.oscModel = SimpleTableModel([
            translate('ControllerOscSettings', 'Path'),
            translate('ControllerOscSettings', 'Types'),
            translate('ControllerOscSettings', 'Actions')])

        self.OscView = OscView(cue_class, parent=self.oscGroup)
        self.OscView.setModel(self.oscModel)
        self.oscGroup.layout().addWidget(self.OscView, 0, 0, 1, 2)

        self.addButton = QPushButton(self.oscGroup)
        self.addButton.clicked.connect(self.__new_message)
        self.oscGroup.layout().addWidget(self.addButton, 1, 0)

        self.removeButton = QPushButton(self.oscGroup)
        self.removeButton.clicked.connect(self.__remove_message)
        self.oscGroup.layout().addWidget(self.removeButton, 1, 1)

        self.oscCapture = QPushButton(self.oscGroup)
        self.oscCapture.clicked.connect(self.capture_message)
        self.oscGroup.layout().addWidget(self.oscCapture, 2, 0)

        self.captureDialog = QDialog()
        self.captureDialog.setWindowTitle(translate('ControllerOscSettings',
                                             'OSC Capture'))
        self.captureDialog.setModal(True)
        self.captureLabel = QLabel('...')
        self.captureDialog.setLayout(QVBoxLayout())
        self.captureDialog.layout().addWidget(self.captureLabel)

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self.captureDialog)
        self.buttonBox.accepted.connect(self.captureDialog.accept)
        self.buttonBox.rejected.connect(self.captureDialog.reject)
        self.captureDialog.layout().addWidget(self.buttonBox)

        self.capturedMessage = {'path': None, 'types': None}

        self.retranslateUi()

        self._default_action = self._cue_class.CueActions[0].name

    def retranslateUi(self):
        self.addButton.setText(translate('ControllerOscSettings', 'Add'))
        self.removeButton.setText(translate('ControllerOscSettings', 'Remove'))
        self.oscCapture.setText(translate('ControllerOscSettings', 'Capture'))

    def enable_check(self, enabled):
        self.oscGroup.setCheckable(enabled)
        self.oscGroup.setChecked(False)

    def get_settings(self):
        settings = {}

        messages = []

        for row in self.oscModel.rows:
            message = Osc.key_from_message(row[0], row[1])
            messages.append((message, row[-1]))

        if messages:
            settings['osc'] = messages

        return settings

    def load_settings(self, settings):
        if 'osc' in settings:
            for options in settings['osc']:
                path, types = Osc.from_key(options[0])
                self.oscModel.appendRow(path, types, options[1])

    def capture_message(self):
        OscCommon().new_message.connect(self.__show_message)
        result = self.captureDialog.exec()
        if result == QDialog.Accepted:
            self.oscModel.appendRow(self.capturedMessage['path'], self.capturedMessage['types'], self._default_action)
        OscCommon().new_message.disconnect(self.__show_message)

    def __show_message(self, path, args, types, src):
        self.capturedMessage['path'] = path
        self.capturedMessage['types'] = types
        self.captureLabel.setText('{0} "{1}" {2}'.format(path, types, args))

    def __new_message(self):
        self.oscModel.appendRow('', '', self._default_action)

    def __remove_message(self):
        self.oscModel.removeRow(self.OscView.currentIndex().row())


class OscView(QTableView):
    def __init__(self, cue_class, **kwargs):
        super().__init__(**kwargs)

        cue_actions = [action.name for action in cue_class.CueActions]
        self.delegates = [LineEditDelegate(),
                          LineEditDelegate(),
                          ComboBoxDelegate(options=cue_actions,
                                           tr_context='CueAction')]

        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)

        self.setShowGrid(False)
        self.setAlternatingRowColors(True)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setHighlightSections(False)

        self.verticalHeader().sectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(24)
        self.verticalHeader().setHighlightSections(False)

        for column, delegate in enumerate(self.delegates):
            self.setItemDelegateForColumn(column, delegate)
