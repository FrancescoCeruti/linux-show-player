# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
# Copyright 2012-2016 Thomas Achtner <info@offtools.de>
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


from enum import Enum

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QGridLayout, \
    QTableView, QTableWidget, QHeaderView, QPushButton, QLabel, \
    QLineEdit, QDoubleSpinBox, QStyledItemDelegate, QCheckbox, QSpinBox

from lisp.ui.widgets import FadeComboBox

from lisp.core.decorators import async
from lisp.core.fader import Fader
from lisp.core.fade_functions import FadeInType, FadeOutType
from lisp.cues.cue import Cue, CueAction
from lisp.ui import elogging
from lisp.ui.qmodels import SimpleTableModel
from lisp.core.has_properties import Property
from lisp.ui.qdelegates import ComboBoxDelegate, LineEditDelegate, \
    CheckBoxDelegate
from lisp.ui.settings.cue_settings import CueSettingsRegistry, \
    SettingsPage
from lisp.modules.osc.osc_common import OscCommon
from lisp.ui.ui_utils import translate

COL_TYPE = 0
COL_START_VAL = 1
COL_END_VAL = 2
COL_DO_FADE = 3

COL_BASE_VAL = 1
COL_DIFF_VAL = 2


class OscMessageType(Enum):
    Int = 'Integer'
    Float = 'Float'
    Bool = 'Bool'
    String = 'String'


def test_path(path):
    if isinstance(path, str):
        if len(path) > 1 and path[0] is '/':
            return True
    return False


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


def guess_end_value(t, value):
    """guess end value for fades"""
    if t == OscMessageType.Int.value:
        start = round(int(value))
        if start < 0:
            return "{0:d}".format(0)
        elif start == 0:
            return "{0:d}".format(255)
        else:
            for i in range(4):
                if start < 0xff << (i * 8):
                    return "{0:d}".format(0xff << (i * 8))
            return "{0:d}".format(0xff << (3 * 8))

    elif t == OscMessageType.Float.value:
        start = float(value)
        if start == 0:
            return "{0:.2f}".format(1)
        elif start < 0:
            return "{0:.2f}".format(0)
        elif start < 1:
            return "{0:.2f}".format(1)
        else:
            return "{0:.2f}".format(1000)
    else:
        return ''


def format_string(t, sarg):
    """checks if string can be converted and formats it"""
    # if len(sarg) == 0:
    #     return ''
    if t == OscMessageType.Int.value:
        return "{0:d}".format(int(sarg))
    elif t == OscMessageType.Float.value:
        return "{0:.2f}".format(float(sarg))
    elif t == OscMessageType.Bool.value:
        if sarg.lower() == 'true':
            return 'True'
        elif sarg.lower() == 'false':
            return 'False'
        if sarg.isdigit():
            return "{0}".format(bool(int(sarg)))
        else:
            return "{0}".format(bool(False))
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = translate('CueName', self.Name)

        self.__fader = Fader(self, '_position')
        self.__value = 0
        self.__fadein = True

        self.__arg_list = []
        self.__has_fade = False

    def __get_position(self):
        return self.__value

    def __set_position(self, value):
        self.__value = value
        args = []
        for row in self.__arg_list:
            if row[COL_DIFF_VAL] > 0:
                args.append(row[COL_BASE_VAL] + row[COL_DIFF_VAL] * self.__value)
            else:
                args.append(row[COL_BASE_VAL])
        OscCommon().send(self.path, *args)

    _position = property(__get_position, __set_position)

    def __init_arguments(self):
        # check path
        if not test_path(self.path):
            return False

        # arguments from the cue settings are converted and stored in a new list
        # list: [ type, base_value, diff_value ]
        self.__arg_list = []
        try:
            for arg in self.args:
                if 'end' in arg and arg['fade']:
                    self.__has_fade = True
                    diff_value = arg['end'] - arg['start']
                    self.__arg_list.append([arg['type'], arg['start'], diff_value])
                else:
                    self.__arg_list.append([arg['type'],
                                            arg['start'],
                                            0])
        except KeyError:
            elogging.error("OSC: could not parse argument list, nothing sent")
            return False

        # set fade type, based on the first argument, which will have a fade
        if self.__has_fade:
            for row in self.__arg_list:
                if row[COL_DIFF_VAL] > 0:
                    self.__fadein = True
                    break
                elif row[COL_DIFF_VAL] < 0:
                    self.__fadein = False
                    break
                else:
                    continue

        # always fade from 0 to 1, reset value before start or restart fade
        self.__value = 0

        return True

    def has_fade(self):
        return self.duration > 0 and self.__has_fade

    def __start__(self, fade=False):
        if self.__init_arguments():
            if self.__fader.is_paused():
                self.__fader.restart()
                return True

            if self.has_fade():
                if not self.__fadein:
                    self.__fade(FadeOutType[self.fade_type])
                    return True
                else:
                    self.__fade(FadeInType[self.fade_type])
                    return True
            else:
                self._position = 1
        else:
            elogging.error("OSC: Error on parsing argument list - nothing sent", dialog=False)

        return False

    def __stop__(self, fade=False):
        self.__fader.stop()
        return True

    def __pause__(self, fade=False):
        self.__fader.pause()
        return True

    __interrupt__ = __stop__

    @async
    def __fade(self, fade_type):
        try:
            self.__fader.prepare()
            ended = self.__fader.fade(round(self.duration / 1000, 2),
                                      1,
                                      fade_type)

            # to avoid approximation problems
            self._position = 1
            if ended:
                self._ended()
        except Exception as e:
            self._error(
                translate('OscCue', 'Error during cue execution'),
                str(e)
            )

    def current_time(self):
        return self.__fader.current_time()


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
            if not test_path(self.pathEdit.text()):
                elogging.error("OSC: Error parsing osc path, removing message")
                return conf

        if not (checkable and not self.oscGroup.isChecked()):
            try:
                conf['path'] = self.pathEdit.text()
                args_list = []
                for row in self.oscModel.rows:
                    arg = {'type': row[COL_TYPE],
                           'start': string_to_value(row[COL_TYPE], row[COL_START_VAL])}

                    if row[COL_END_VAL]:
                        arg['end'] = string_to_value(row[COL_TYPE], row[COL_END_VAL])

                    arg['fade'] = row[COL_DO_FADE]
                    args_list.append(arg)

                conf['args'] = args_list
            except ValueError:
                elogging.error("OSC: Error parsing osc arguments, removing message")
                return {}

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
            for arg in args:
                self.oscModel.appendRow(arg['type'],
                                        str(arg['start']),
                                        str(arg['end']) if 'end' in arg else '',
                                        arg['fade'])

        self.fadeSpin.setValue(settings.get('duration', 0) / 1000)
        self.fadeCurveCombo.setCurrentType(settings.get('fade_type', ''))

    def __new_argument(self):
        self.oscModel.appendRow(OscMessageType.Int.value, '0', '', False)

    def __remove_argument(self):
        if self.oscModel.rowCount():
            self.oscModel.removeRow(self.oscView.currentIndex().row())

    def __test_message(self):
        # TODO: check arguments for error

        path = self.pathEdit.text()

        if not test_path(path):
            elogging.warning("OSC: no valid path for OSC message - nothing sent",
                             details="Path should start with a '/' followed by a name.",
                             dialog=True)
            return

        try:
            args = []
            for row in self.oscModel.rows:
                if row[COL_END_VAL] and row[COL_DO_FADE]:
                    args.append(string_to_value(row[COL_TYPE], row[COL_END_VAL]))
                else:
                    args.append(string_to_value(row[COL_TYPE], row[COL_START_VAL]))

            OscCommon().send(path, *args)
        except ValueError:
            elogging.error("OSC: Error on parsing argument list - nothing sent")

    @staticmethod
    def __argument_changed(index_topleft, index_bottomright, roles):
        if not (Qt.EditRole in roles):
            return

        model = index_bottomright.model()
        curr_row = index_topleft.row()
        model_row = model.rows[curr_row]
        curr_col = index_bottomright.column()

        osctype = model_row[COL_TYPE]
        start = model_row[COL_START_VAL]
        end = model_row[COL_END_VAL]

        # check message
        if curr_col == COL_TYPE:
            # format start value
            try:
                model_row[COL_START_VAL] = format_string(osctype, start)
            except ValueError:
                model_row[COL_START_VAL] = format_string(osctype, 0)
                elogging.warning("OSC Argument Error", details="start value {0} is not a {1}".format(start, osctype),
                                 dialog=True)
            # if end value: format end value or remove if nonfade type
            if not type_can_fade(osctype):
                model_row[COL_END_VAL] = ''
                model_row[COL_DO_FADE] = False
            else:
                if model_row[COL_END_VAL]:
                    try:
                        model_row[COL_END_VAL] = format_string(osctype, end)
                    except ValueError:
                        model_row[COL_END_VAL] = ''
                        elogging.warning("OSC Argument Error",
                                         details="end value {0} is not a {1}".format(end, osctype), dialog=True)

        elif curr_col == COL_START_VAL:
            # format start value
            try:
                model_row[COL_START_VAL] = format_string(osctype, start)
            except ValueError:
                model_row[COL_START_VAL] = format_string(osctype, '0')
                elogging.warning("OSC Argument Error", details="{0} not a {1}".format(start, osctype), dialog=True)

        elif curr_col == COL_END_VAL:
            # check if type can fade
            if not type_can_fade(osctype):
                model_row[COL_END_VAL] = ''
                elogging.warning("OSC Argument Error", details="cannot fade {0}".format(osctype), dialog=True)
            else:
                # format end value
                if model_row[COL_DO_FADE]:
                    try:
                        model_row[COL_END_VAL] = format_string(osctype, end)
                    except ValueError:
                        model_row[COL_END_VAL] = guess_end_value(osctype, model_row[COL_START_VAL])
                        elogging.warning("OSC Argument Error", details="{0} not a {1}".format(end, osctype), dialog=True)
                else:
                    if model_row[COL_END_VAL]:
                        try:
                            model_row[COL_END_VAL] = format_string(osctype, end)
                        except ValueError:
                            model_row[COL_END_VAL] = guess_end_value(osctype,
                                                                                model_row[COL_START_VAL])
                            elogging.warning("OSC Argument Error", details="{0} not a {1}".format(end, osctype),
                                             dialog=True)

        elif curr_col == COL_DO_FADE:
            # fade is True
            if model_row[COL_DO_FADE] is True:
                if not type_can_fade(osctype):
                    elogging.warning("OSC Argument Error", details="cannot fade {0}".format(osctype), dialog=True)
                    model_row[COL_DO_FADE] = False
                else:
                    if not model_row[COL_END_VAL]:
                        model_row[COL_END_VAL] = guess_end_value(osctype, model_row[COL_START_VAL])
                        elogging.warning("OSC Argument Error", details="fades need an end value", dialog=True)
            else:
                model_row[COL_END_VAL] = ''
        else:
            raise RuntimeError("OSC: ModelIndex Error")


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
