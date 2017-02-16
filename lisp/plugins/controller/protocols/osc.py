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


import ast

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import QGroupBox, QPushButton, QVBoxLayout, \
    QTableView, QTableWidget, QHeaderView, QGridLayout, QLabel, \
    QDialog, QDialogButtonBox, QLineEdit

from lisp.modules import check_module
from lisp.modules.osc.osc_common import OscCommon
from lisp.ui.qdelegates import OscArgumentDelegate
from lisp.modules.osc.osc_common import OscMessageType
from lisp.plugins.controller.protocols.protocol import Protocol
from lisp.ui.qdelegates import ComboBoxDelegate, LineEditDelegate
from lisp.ui.qmodels import SimpleTableModel
from lisp.ui.settings.settings_page import CueSettingsPage
from lisp.ui.ui_utils import translate
from lisp.ui import elogging


class Osc(Protocol):
    def __init__(self):
        super().__init__()

        if check_module('osc') and OscCommon().listening:
            OscCommon().new_message.connect(self.__new_message)

    def __new_message(self, path, args, types):
        key = Osc.key_from_message(path, types, args)
        self.protocol_event.emit(key)

    @staticmethod
    def key_from_message(path, types, args):
        key = [path, types, *args]
        return 'OSC{}'.format(key)

    @staticmethod
    def key_from_values(path, types, args):
        if not len(types):
            return "OSC['{0}', '{1}']".format(path, types)
        else:
            return "OSC['{0}', '{1}', {2}]".format(path, types, args)

    @staticmethod
    def message_from_key(key):
        key = ast.literal_eval(key[3:])
        return key


class OscMessageDialog(QDialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setMaximumSize(500, 300)
        self.setMinimumSize(500, 300)
        self.resize(500, 300)

        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.groupBox = QGroupBox(self)
        self.groupBox.setLayout(QGridLayout())
        self.layout().addWidget(self.groupBox)

        self.pathLabel = QLabel()
        self.groupBox.layout().addWidget(self.pathLabel, 0, 0, 1, 2)

        self.pathEdit = QLineEdit()
        self.groupBox.layout().addWidget(self.pathEdit, 1, 0, 1, 2)

        self.model = SimpleTableModel([
            translate('Osc Cue', 'Type'),
            translate('Osc Cue', 'Argument')])

        self.model.dataChanged.connect(self.__argument_changed)

        self.view = OscArgumentView(parent=self.groupBox)
        self.view.setModel(self.model)
        self.groupBox.layout().addWidget(self.view, 2, 0, 1, 2)

        self.buttons = QDialogButtonBox(self)
        self.buttons.addButton(QDialogButtonBox.Cancel)
        self.buttons.addButton(QDialogButtonBox.Ok)
        self.layout().addWidget(self.buttons)

        self.addButton = QPushButton(self.groupBox)
        self.addButton.clicked.connect(self.__add_argument)
        self.groupBox.layout().addWidget(self.addButton, 3, 0)

        self.removeButton = QPushButton(self.groupBox)
        self.removeButton.clicked.connect(self.__remove_argument)
        self.groupBox.layout().addWidget(self.removeButton, 3, 1)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.retranslateUi()

    def __add_argument(self):
        self.model.appendRow(OscMessageType.Int.value, 0)

    def __remove_argument(self):
        if self.model.rowCount() and self.view.currentIndex().row():
            self.model.removeRow(self.view.currentIndex().row())

    def __argument_changed(self, index_topleft, index_bottomright, roles):
        if not (Qt.EditRole in roles):
            return

        model = index_bottomright.model()
        curr_row = index_topleft.row()
        model_row = model.rows[curr_row]
        curr_col = index_bottomright.column()
        osc_type = model_row[0]

        if curr_col == 0:
            index = model.createIndex(curr_row, 1)
            delegate = self.view.itemDelegate(index)
            delegate.updateEditor(OscMessageType[osc_type])

            if osc_type == 'Integer' or osc_type == 'Float':
                model_row[1] = 0
            elif osc_type == 'Bool':
                model_row[1] = True
            else:
                model_row[1] = ''

    def retranslateUi(self):
        self.groupBox.setTitle(translate('ControllerOscSettings', 'OSC Message'))
        self.pathLabel.setText(translate('ControllerOscSettings', 'OSC Path: (example: "/path/to/something")'))
        self.addButton.setText(translate('OscCue', 'Add'))
        self.removeButton.setText(translate('OscCue', 'Remove'))


class OscArgumentView(QTableView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.delegates = [ComboBoxDelegate(options=[i.value for i in OscMessageType],
                                           tr_context='OscMessageType'),
                          OscArgumentDelegate()]

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
            translate('ControllerOscSettings', 'Arguments'),
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

        self.captureDialog = QDialog(self, flags=Qt.Dialog)
        self.captureDialog.resize(300, 150)
        self.captureDialog.setMaximumSize(self.captureDialog.size())
        self.captureDialog.setMinimumSize(self.captureDialog.size())
        self.captureDialog.setWindowTitle(translate('ControllerOscSettings', 'OSC Capture'))
        self.captureDialog.setModal(True)
        self.captureLabel = QLabel('Waiting for message:')
        self.captureLabel.setAlignment(Qt.AlignCenter)
        self.captureDialog.setLayout(QVBoxLayout())
        self.captureDialog.layout().addWidget(self.captureLabel)

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self.captureDialog)
        self.buttonBox.accepted.connect(self.captureDialog.accept)
        self.buttonBox.rejected.connect(self.captureDialog.reject)
        self.captureDialog.layout().addWidget(self.buttonBox)

        self.capturedMessage = {'path': None, 'types': None, 'args': None}

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
            key = Osc.key_from_values(row[0], row[1], row[2])
            messages.append((key, row[-1]))

        if messages:
            settings['osc'] = messages

        return settings

    def load_settings(self, settings):
        if 'osc' in settings:
            for options in settings['osc']:
                key = Osc.message_from_key(options[0])
                self.oscModel.appendRow(key[0],
                                        key[1],
                                        '{}'.format(key[2:])[1:-1],
                                        options[1])

    def capture_message(self):
        OscCommon().new_message.connect(self.__show_message)
        result = self.captureDialog.exec()
        if result == QDialog.Accepted and self.capturedMessage['path']:
            args = '{}'.format(self.capturedMessage['args'])[1:-1]
            self.oscModel.appendRow(self.capturedMessage['path'],
                                    self.capturedMessage['types'],
                                    args,
                                    self._default_action)
        OscCommon().new_message.disconnect(self.__show_message)
        self.captureLabel.setText('Waiting for message:')

    def __show_message(self, path, args, types):
        self.capturedMessage['path'] = path
        self.capturedMessage['types'] = types
        self.capturedMessage['args'] = args
        self.captureLabel.setText('OSC: "{0}" "{1}" {2}'.format(self.capturedMessage['path'],
                                                                self.capturedMessage['types'],
                                                                self.capturedMessage['args']))

    def __new_message(self):
        dialog = OscMessageDialog(parent=self)
        if dialog.exec_() == dialog.Accepted:
            path = dialog.pathEdit.text()
            if len(path) < 2 or path[0] is not '/':
                elogging.warning('OSC: Osc path seems not valid,\ndo not forget to edit the path later.',
                                 dialog=True)
            types = ''
            arguments = []
            for row in dialog.model.rows:
                if row[0] == 'Bool':
                    if row[1] is True:
                        types += 'T'
                    if row[1] is True:
                        types += 'F'
                else:
                    if row[0] == 'Integer':
                        types += 'i'
                    elif row[0] == 'Float':
                        types += 'f'
                    elif row[0] == 'String':
                        types += 's'
                    else:
                        raise TypeError('Unsupported Osc Type')
                    arguments.append(row[1])

            self.oscModel.appendRow(path, types, '{}'.format(arguments)[1:-1], self._default_action)

    def __remove_message(self):
        if self.oscModel.rowCount() and self.OscView.currentIndex().row():
            self.oscModel.removeRow(self.OscView.currentIndex().row())


class OscView(QTableView):
    def __init__(self, cue_class, **kwargs):
        super().__init__(**kwargs)

        cue_actions = [action.name for action in cue_class.CueActions]
        self.delegates = [LineEditDelegate(),
                          LineEditDelegate(),
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
