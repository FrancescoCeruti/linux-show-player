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

# TODO: proper Test for Format, add Error Dialog, Cue Test-Button in Settings

from enum import Enum
from time import sleep

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QGridLayout, \
    QTableView, QTableWidget, QHeaderView, QPushButton, QLabel, \
    QLineEdit

from lisp.core.decorators import async, locked_method
from lisp.core.fade_functions import ntime, FadeInType, FadeOutType
from lisp.core.fader import Fader
from lisp.cues.cue import Cue, CueState, CueAction
from lisp.ui import elogging
from lisp.ui.qmodels import SimpleTableModel
from lisp.core.has_properties import Property
from lisp.ui.qdelegates import ComboBoxDelegate, LineEditDelegate,\
    CheckBoxDelegate
from lisp.cues.cue import Cue, CueState
from lisp.ui.settings.cue_settings import CueSettingsRegistry,\
    SettingsPage
from lisp.modules.osc.osc_common import OscCommon
from lisp.ui.ui_utils import translate

COL_TYPE = 0
COL_START_VAL = 1
COL_END_VAL = 2
COL_DO_FADE = 3

class OscMessageType(Enum):
    Int = 'Integer'
    Float = 'Float'
    Bool = 'Bool'
    String = 'String'


def string_to_value(t, sarg):
    """converts string to requested value for given type"""
    if t == OscMessageType.Int.value:
        return int(sarg)
    elif t == OscMessageType.Float.value:
        return float(sarg)
    elif t == OscMessageType.Bool.value:
        if sarg.lower() == 'true':
            return True
        elif sarg.lower() == 'false':
            return False
        else:
            return bool(int(sarg))
    elif t == OscMessageType.String.value:
        return str(sarg)
    else:
        raise ValueError


def format_string(t, sarg):
    """checks if string can be converted and formats it"""
    if len(sarg) == 0:
        return ''
    elif t == OscMessageType.Int.value:
        return "{0:d}".format(int(sarg))
    elif t == OscMessageType.Float.value:
        return "{0:.2f}".format(int(sarg))
    elif t == OscMessageType.Bool.value:
        if sarg.lower() == 'true':
            return 'True'
        elif sarg.lower() == 'false':
            return 'False'
        else:
            return "{0}".format(bool(int(sarg)))
    elif t == OscMessageType.String.value:
        return "{0}".format(sarg)
    else:
        raise ValueError


def can_fade(t):
    if t == OscMessageType.Int.value:
        return True
    elif t == OscMessageType.Float.value:
        return True
    else:
        return False


class OscCue(Cue):
    Name = QT_TRANSLATE_NOOP('CueName', 'OSC Cue')

    CueActions = (CueAction.Default, CueAction.Start, CueAction.FadeInStart,
                  CueAction.Stop, CueAction.FadeOutStop, CueAction.Pause,
                  CueAction.FadeOutPause)

    path = Property(default='')
    args = Property(default=[])

    # one global fader used for all faded arguments
    position = Property(default=0.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.__in_fadein = False
        self.__in_fadeout = False
        self.__fader = Fader(self, 'position')
        self.changed('position').connect(self.__send_fade)

    def __send_fade(self):
        print("OSC fade position:", self.position)

    def __start__(self, fade=False):
        if fade and self._can_fadein():
            # Proceed fadein
            self._fadein()
            return True
        else:
            # Single Shot
            value_list = []

            if len(self.path) < 2 or self.path[0] != '/':
                elogging.warning("OSC: no valid path for OSC message - nothing sent", dialog=False)
                return
            try:
                for arg in self.args:
                    value = string_to_value(arg[COL_TYPE], arg[COL_START_VAL])
                    value_list.append(value)
                OscCommon().send(self.path, *value_list)
            except ValueError:
                elogging.warning("OSC: Error on parsing argument list - nothing sent", dialog=False)

            return False

    def __stop__(self, fade=False):
        return True

    def __pause__(self, fade=False):
        return True

    def _can_fade(self):
        has_fade = False
        for arg in self.args:
            if arg[COL_DO_FADE]:
                has_fade = True
                break
        return has_fade

    def _can_fadein(self):
        return self._can_fade() and self.fadein_duration > 0

    def _can_fadeout(self):
        return self._can_fade() and self.fadeout_duration > 0

    @async
    def _fadein(self):
        if self._can_fadein():
            self.__in_fadein = True
            self.fadein_start.emit()
            try:
                self.__fader.prepare()
                self.__fader.fade(self.fadein_duration,
                                  1.0,
                                  FadeInType[self.fadein_type])
            finally:
                self.__in_fadein = False
                self.fadein_end.emit()

    def _fadeout(self):
        ended = True
        return ended


class OscCueSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP('Cue Name', 'OSC Settings')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.oscGroup = QGroupBox(self)
        self.oscGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.oscGroup)

        self.pathLabel = QLabel()
        self.oscGroup.layout().addWidget(self.pathLabel, 0, 0)

        self.pathEdit = QLineEdit()
        self.oscGroup.layout().addWidget(self.pathEdit, 1, 0, 1, 2)

        self.oscModel = SimpleTableModel([
            translate('Osc Cue', 'Type'),
            translate('Osc Cue', 'Argument'),
            translate('Osc Cue', 'FadeTo'),
            translate('Osc Cue', 'Fade')])

        self.oscModel.dataChanged.connect(self.__argument_changed)

        self.oscView = OscView(parent=self.oscGroup)
        self.oscView.setModel(self.oscModel)
        self.oscGroup.layout().addWidget(self.oscView, 2, 0, 1, 2)

        self.addButton = QPushButton(self.oscGroup)
        self.addButton.clicked.connect(self.__new_argument)
        self.oscGroup.layout().addWidget(self.addButton, 3, 0)

        self.removeButton = QPushButton(self.oscGroup)
        self.removeButton.clicked.connect(self.__remove_argument)
        self.oscGroup.layout().addWidget(self.removeButton, 3, 1)

        self.testButton = QPushButton(self.oscGroup)
        self.testButton.clicked.connect(self.__test_message)
        self.oscGroup.layout().addWidget(self.testButton, 4, 0)

        self.retranslateUi()

    def retranslateUi(self):
        self.oscGroup.setTitle(translate('OscCue', 'OSC Message'))
        self.addButton.setText(translate('OscCue', 'Add'))
        self.removeButton.setText(translate('OscCue', 'Remove'))
        self.testButton.setText(translate('OscCue', 'Test'))
        self.pathLabel.setText(translate('OscCue', 'OSC Path: (example: "/path/to/something")'))

    def get_settings(self):
        oscmsg = {'path': self.pathEdit.text(),
                  'args': [row for row in self.oscModel.rows]}
        return oscmsg

    def load_settings(self, settings):
        if 'path' in settings:
            path = settings.get('path', '')
            self.pathEdit.setText(path)
            if 'args' in settings:
                args = settings.get('args', '')
                for row in args:
                    self.oscModel.appendRow(row[0], row[1], row[2], row[3])

    def __new_argument(self):
        self.oscModel.appendRow(OscMessageType.Int.value, '', '', False)

    def __remove_argument(self):
        if self.oscModel.rowCount():
            self.oscModel.removeRow(self.oscView.currentIndex().row())

    def __test_message(self):
        oscmsg = {'path': self.pathEdit.text(),
                  'args': [row for row in self.oscModel.rows]}
        value_list = []
        if len(oscmsg['path']) < 2:
            elogging.warning("OSC: no valid path for OSC message - nothing sent",
                             details="Path too short.",
                             dialog=True)
            return

        if oscmsg['path'][0] != '/':
            elogging.warning("OSC: no valid path for OSC message - nothing",
                             details="Path should start with '/'.",
                             dialog=True)
            return

        try:
            for arg in oscmsg['args']:
                value = string_to_value(arg[0], arg[1])
                value_list.append(value)
            OscCommon().send(oscmsg['path'], *value_list)
        except ValueError:
            elogging.warning("OSC: Error on parsing argument list - nothing sent")

    def __argument_changed(self, index_topleft, index_bottomright, roles):
        model = index_bottomright.model()
        osctype = model.rows[index_bottomright.row()][0]
        start = model.rows[index_bottomright.row()][1]
        end = model.rows[index_bottomright.row()][2]

        try:
            model.rows[index_bottomright.row()][1] = format_string(osctype, start)
        except ValueError:
            model.rows[index_bottomright.row()][1] = ''
            elogging.warning("OSC Argument Error", details="{0} not a {1}".format(start, osctype), dialog=True)

        try:
            model.rows[index_bottomright.row()][2] = format_string(osctype, end)
        except ValueError:
            model.rows[index_bottomright.row()][2] = ''
            elogging.warning("OSC Argument Error", details="{0} not a {1}".format(end, osctype), dialog=True)

        if not can_fade(osctype):
            model.rows[index_bottomright.row()][3] = False


class OscView(QTableView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.delegates = [ComboBoxDelegate(options=[i.value for i in OscMessageType],
                                           tr_context='OscMessageType'),
                          LineEditDelegate(),
                          LineEditDelegate(),
                          CheckBoxDelegate()]

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

CueSettingsRegistry().add_item(OscCueSettings, OscCue)
