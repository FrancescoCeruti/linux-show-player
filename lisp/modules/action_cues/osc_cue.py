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

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QGridLayout, \
    QTableView, QTableWidget, QHeaderView, QPushButton, QLabel, \
    QLineEdit, QDoubleSpinBox

from lisp.ui.widgets import FadeComboBox

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

COL_BASE_VAL = 1
COL_DIFF_VAL = 2
COL_FUNCTOR = 3


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


def convert_value(t, value):
    """converts value to requested value for given type"""
    if t == OscMessageType.Int.value:
        return round(int(value))
    elif t == OscMessageType.Float.value:
        return float(value)
    elif t == OscMessageType.Bool.value:
        return bool(value)
    elif t == OscMessageType.String.value:
        return str(value)
    else:
        raise ValueError


def format_string(t, sarg):
    """checks if string can be converted and formats it"""
    if len(sarg) == 0:
        return ''
    elif t == OscMessageType.Int.value:
        return "{0:d}".format(int(sarg))
    elif t == OscMessageType.Float.value:
        return "{0:.2f}".format(float(sarg))
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


def type_can_fade(t):
    if t == OscMessageType.Int.value:
        return True
    elif t == OscMessageType.Float.value:
        return True
    else:
        return False


class OscCue(Cue):
    Name = QT_TRANSLATE_NOOP('CueName', 'OSC Cue')

    CueActions = (CueAction.Default, CueAction.Start, CueAction.Stop,
                  CueAction.Pause)

    path = Property(default='')
    args = Property(default=[])
    fade_type = Property(default=FadeInType.Linear.name)

    # one global fader used for all faded arguments
    position = Property(default=0.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = translate('CueName', self.Name)

        self.__fade_args = None
        self.__time = 0
        self.__stop = False
        self.__pause = False

    def __prepare_fade(self):
        """ returns list of arguments, that will be faded
            each item of the list contains:
            message type tag, start value, diff value, fade functor
            start and end value are converted from strings to the
            type to the correct type (message type tag)
        """
        value_list = []
        for arg in self.args:
            if not arg[COL_END_VAL] or not arg[COL_DO_FADE]:
                value_list.append([arg[COL_TYPE],
                                   string_to_value(arg[COL_TYPE], arg[COL_BASE_VAL]),
                                   0,
                                   None])
            else:
                base_value = string_to_value(arg[COL_TYPE], arg[COL_START_VAL])
                diff_value = string_to_value(arg[COL_TYPE], arg[COL_END_VAL]) - base_value
                if arg[COL_DO_FADE] and abs(diff_value):
                    fade_arg = []
                    fade_arg.append(arg[COL_TYPE])
                    fade_arg.append(base_value)
                    fade_arg.append(diff_value)
                    if diff_value > 0:
                        fade_arg.append(FadeInType[self.fade_type].value)
                    else:
                        fade_arg.append(FadeOutType[self.fade_type].value)
                    value_list.append(fade_arg)
        return value_list

    def __start__(self, fade=False):
        self.__fade_args = self.__prepare_fade()
        if self.__can_fade():
            self.__send_fade()
            return True
        else:
            self.__send_single_shot()

        return False

    def __send_single_shot(self):
        value_list = []

        if len(self.path) < 2 or self.path[0] != '/':
            elogging.warning("OSC: no valid path for OSC message - nothing sent", dialog=False)
            return False
        try:
            for arg in self.args:
                value = string_to_value(arg[COL_TYPE], arg[COL_START_VAL])
                value_list.append(value)
            OscCommon().send(self.path, *value_list)
        except ValueError:
            elogging.warning("OSC: Error on parsing argument list - nothing sent", dialog=False)

        return False

    @async
    @locked_method
    def __send_fade(self):
        self.__stop = False
        self.__pause = False

        try:
            begin = self.__time
            duration = (self.duration // 10)

            while (not (self.__stop or self.__pause) and
                           self.__time <= duration):
                time = ntime(self.__time, begin, duration)

                value_list = []
                for arg in self.__fade_args:
                    if arg[COL_DIFF_VAL]:
                        functor = arg[COL_FUNCTOR]
                        current = functor(time, arg[COL_DIFF_VAL], arg[COL_BASE_VAL])
                        value_list.append(convert_value(arg[COL_TYPE], current))
                    else:
                        value_list.append(convert_value(arg[COL_TYPE], arg[COL_BASE_VAL]))

                OscCommon().send(self.path, *value_list)

                self.__time += 1
                sleep(0.01)

            if not self.__pause:
                # to avoid approximation problems
                # self.__send_single_shot() # but with end value
                if not self.__stop:
                    self._ended()

        except Exception as e:
            self._error(
                translate('OscCue', 'Error during cue execution'),
                str(e)
            )
        finally:
            if not self.__pause:
                self.__time = 0

    def __stop__(self, fade=False):
        self.__stop = True
        return True

    def __pause__(self, fade=False):
        self.__pause = True
        return True

    def __can_fade(self):
        return self.__fade_args and self.duration > 0

    def current_time(self):
        return self.__time * 10

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

        # Fade
        self.fadeGroup = QGroupBox(self)
        self.fadeGroup.setLayout(QGridLayout())
        self.layout().addWidget(self.fadeGroup)

        self.fadeSpin = QDoubleSpinBox(self.fadeGroup)
        self.fadeSpin.setMaximum(3600)
        self.fadeGroup.layout().addWidget(self.fadeSpin, 0, 0)

        self.fadeLabel = QLabel(self.fadeGroup)
        self.fadeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.fadeGroup.layout().addWidget(self.fadeLabel, 0, 1)

        self.fadeCurveCombo = FadeComboBox(parent=self.fadeGroup)
        self.fadeGroup.layout().addWidget(self.fadeCurveCombo, 1, 0)

        self.fadeCurveLabel = QLabel(self.fadeGroup)
        self.fadeCurveLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.fadeGroup.layout().addWidget(self.fadeCurveLabel, 1, 1)

        self.retranslateUi()

    def retranslateUi(self):
        self.oscGroup.setTitle(translate('OscCue', 'OSC Message'))
        self.addButton.setText(translate('OscCue', 'Add'))
        self.removeButton.setText(translate('OscCue', 'Remove'))
        self.testButton.setText(translate('OscCue', 'Test'))
        self.pathLabel.setText(translate('OscCue', 'OSC Path: (example: "/path/to/something")'))
        self.fadeGroup.setTitle(translate('OscCue', 'Fade'))
        self.fadeLabel.setText(translate('OscCue', 'Time (sec)'))
        self.fadeCurveLabel.setText(translate('OscCue', 'Curve'))

    def enable_check(self, enabled):
        self.oscGroup.setCheckable(enabled)
        self.oscGroup.setChecked(False)

        self.fadeGroup.setCheckable(enabled)
        self.fadeGroup.setChecked(False)

    def get_settings(self):
        conf = {}
        checkable = self.oscGroup.isCheckable()

        if not (checkable and not self.oscGroup.isChecked()):
            conf['path'] = self.pathEdit.text()
            conf['args'] = [row for row in self.oscModel.rows]
        if not (checkable and not self.fadeGroup.isCheckable()):
            conf['duration'] = self.fadeSpin.value() * 1000
            conf['fade_type'] = self.fadeCurveCombo.currentType()
        return conf

    def load_settings(self, settings):
        if 'path' in settings:
            path = settings.get('path', '')
            self.pathEdit.setText(path)
            if 'args' in settings:
                args = settings.get('args', '')
                for row in args:
                    self.oscModel.appendRow(row[0], row[1], row[2], row[3])
            self.fadeSpin.setValue(settings.get('duration', 0) / 1000)
            self.fadeCurveCombo.setCurrentType(settings.get('fade_type', ''))

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
        osctype = model.rows[index_bottomright.row()][COL_TYPE]
        start = model.rows[index_bottomright.row()][COL_START_VAL]
        end = model.rows[index_bottomright.row()][COL_END_VAL]

        # test Start value for correct format
        try:
            model.rows[index_bottomright.row()][COL_START_VAL] = format_string(osctype, start)
        except ValueError:
            model.rows[index_bottomright.row()][COL_START_VAL] = ''
            elogging.warning("OSC Argument Error", details="{0} not a {1}".format(start, osctype), dialog=True)

        # test End value for correct format
        try:
            model.rows[index_bottomright.row()][COL_END_VAL] = format_string(osctype, end)
        except ValueError:
            model.rows[index_bottomright.row()][COL_END_VAL] = ''
            elogging.warning("OSC Argument Error", details="{0} not a {1}".format(end, osctype), dialog=True)

        # Fade only enabled for Int and Float
        if not type_can_fade(osctype):
            model.rows[index_bottomright.row()][COL_DO_FADE] = False

        # for Fade, test if end value is provided
        if not model.rows[index_bottomright.row()][COL_END_VAL]and \
                model.rows[index_bottomright.row()][COL_DO_FADE]:
            elogging.warning("OSC Argument Error", details="FadeOut value is missing", dialog=True)
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
