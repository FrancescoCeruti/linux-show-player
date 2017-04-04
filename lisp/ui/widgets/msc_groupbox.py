# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2017 Francesco Ceruti <ceppofrancy@gmail.com>
# Copyright 2017 Thomas Achtner <info@offtools.de>
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

import functools

from PyQt5.QtCore import QTime
from PyQt5.QtWidgets import QGroupBox, QGridLayout, QLabel, \
    QComboBox, QSpinBox, QDoubleSpinBox, QFrame, QCheckBox, QTimeEdit

from lisp.ui.ui_utils import translate
from lisp.modules.midi.midi_msc import MscMessage, MscCommand, \
    MscCommandFormat, MscArgument, MscTimeType


class MscGroupBox(QGroupBox):

    DATA_WIDGET = 0
    CHECK_WIDGET = 1

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setLayout(QGridLayout())
        self.layout().setColumnStretch(0, 10)
        self.layout().setColumnStretch(1, 10)
        self.layout().setColumnStretch(2, 1)

        # Device ID
        self.__mscDeviceLabel = QLabel(self)
        self.layout().addWidget(self.__mscDeviceLabel, 0, 0)
        self.__mscDeviceSpin = QSpinBox(self)
        self.__mscDeviceSpin.setRange(0, 127)
        self.__mscDeviceSpin.setValue(0)
        self.__mscDeviceSpin.valueChanged.connect(self.__show_messsage)
        self.layout().addWidget(self.__mscDeviceSpin, 0, 1, 1, 2)

        self.__mscCmdFmtLabel = QLabel(self)
        self.layout().addWidget(self.__mscCmdFmtLabel, 1, 0)
        self.__mscCmdFmtCombo = QComboBox(self)
        self.__mscCmdFmtCombo.addItems([str(i) for i in MscCommandFormat])
        self.__mscCmdFmtCombo.currentTextChanged.connect(self.__show_messsage)
        self.layout().addWidget(self.__mscCmdFmtCombo, 1, 1, 1, 2)

        self.__mscCommandLabel = QLabel(self)
        self.layout().addWidget(self.__mscCommandLabel, 2, 0)
        self.__mscCommandCombo = QComboBox(self)
        self.__mscCommandCombo.addItems([str(i) for i in MscCommand])
        self.__mscCommandCombo.currentTextChanged.connect(self.__type_changed)
        self.__mscCommandCombo.currentTextChanged.connect(self.__show_messsage)
        self.layout().addWidget(self.__mscCommandCombo, 2, 1, 1, 2)

        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.layout().addWidget(line, 3, 0, 1, 3)

        # Data widgets
        self.__data_widgets = {}

        self.__mscQNumberLabel = QLabel(self)
        self.layout().addWidget(self.__mscQNumberLabel, 4, 0)
        self.__mscQNumberSpin = QDoubleSpinBox(self)
        self.__mscQNumberSpin.setRange(0, 999)
        self.__mscQNumberSpin.setDecimals(3)
        self.__mscQNumberSpin.setSingleStep(1.0)
        self.__mscQNumberSpin.setValue(0)
        self.__mscQNumberSpin.valueChanged.connect(self.__show_messsage)
        self.layout().addWidget(self.__mscQNumberSpin, 4, 1)
        self.__mscQNumberCheck = QCheckBox(self)
        self.__mscQNumberCheck.toggled.connect(functools.partial(self.__checked, MscArgument.Q_NUMBER))
        self.layout().addWidget(self.__mscQNumberCheck, 4, 2)
        self.__data_widgets[MscArgument.Q_NUMBER] = [self.__mscQNumberSpin, self.__mscQNumberCheck]

        self.__mscQListLabel = QLabel(self)
        self.layout().addWidget(self.__mscQListLabel, 5, 0)
        self.__mscQListSpin = QDoubleSpinBox(self)
        self.__mscQListSpin.setRange(0, 999)
        self.__mscQListSpin.setDecimals(3)
        self.__mscQListSpin.setSingleStep(1.0)
        self.__mscQListSpin.setValue(0)
        self.__mscQListSpin.valueChanged.connect(self.__show_messsage)
        self.layout().addWidget(self.__mscQListSpin, 5, 1)
        self.__mscQListCheck = QCheckBox(self)
        self.__mscQListCheck.toggled.connect(functools.partial(self.__checked, MscArgument.Q_LIST))
        self.layout().addWidget(self.__mscQListCheck, 5, 2)
        self.__data_widgets[MscArgument.Q_LIST] = [self.__mscQListSpin, self.__mscQListCheck]

        self.__mscQPathLabel = QLabel(self)
        self.layout().addWidget(self.__mscQPathLabel, 6, 0)
        self.__mscQPathSpin = QDoubleSpinBox(self)
        self.__mscQPathSpin.setRange(0, 999)
        self.__mscQPathSpin.setDecimals(3)
        self.__mscQPathSpin.setSingleStep(1.0)
        self.__mscQPathSpin.setValue(0)
        self.__mscQPathSpin.valueChanged.connect(self.__show_messsage)
        self.layout().addWidget(self.__mscQPathSpin, 6, 1)
        self.__mscQPathCheck = QCheckBox(self)
        self.__mscQPathCheck.toggled.connect(functools.partial(self.__checked, MscArgument.Q_PATH))
        self.layout().addWidget(self.__mscQPathCheck, 6, 2)
        self.__data_widgets[MscArgument.Q_PATH] = [self.__mscQPathSpin, self.__mscQPathCheck]

        self.__mscMacroLabel = QLabel(self)
        self.layout().addWidget(self.__mscMacroLabel, 7, 0)
        self.__mscMacroSpin = QSpinBox(self)
        self.__mscMacroSpin.setRange(0, 127)
        self.__mscMacroSpin.setValue(0)
        self.__mscMacroSpin.valueChanged.connect(self.__show_messsage)
        self.layout().addWidget(self.__mscMacroSpin, 7, 1)
        self.__mscMacroCheck = QCheckBox(self)
        self.__mscMacroCheck.toggled.connect(functools.partial(self.__checked, MscArgument.MACRO_NUM))
        self.layout().addWidget(self.__mscMacroCheck, 7, 2)
        self.__data_widgets[MscArgument.MACRO_NUM] = [self.__mscMacroSpin, self.__mscMacroCheck]

        self.__mscCtrlNumLabel = QLabel(self)
        self.layout().addWidget(self.__mscCtrlNumLabel, 8, 0)
        self.__mscCtrlNumSpin = QSpinBox(self)
        self.__mscCtrlNumSpin.setRange(0, 1023)
        self.__mscCtrlNumSpin.setValue(0)
        self.__mscCtrlNumSpin.valueChanged.connect(self.__show_messsage)
        self.layout().addWidget(self.__mscCtrlNumSpin, 8, 1)
        self.__mscCtrlNumCheck = QCheckBox(self)
        self.__mscCtrlNumCheck.toggled.connect(functools.partial(self.__checked, MscArgument.CTRL_NUM))
        self.layout().addWidget(self.__mscCtrlNumCheck, 8, 2)
        self.__data_widgets[MscArgument.CTRL_NUM] = [self.__mscCtrlNumSpin, self.__mscCtrlNumCheck]

        self.__mscCtrlValLabel = QLabel(self)
        self.layout().addWidget(self.__mscCtrlValLabel, 9, 0)
        self.__mscCtrlValSpin = QSpinBox(self)
        self.__mscCtrlValSpin.setRange(0, 1023)
        self.__mscCtrlValSpin.setValue(0)
        self.__mscCtrlValSpin.valueChanged.connect(self.__show_messsage)
        self.layout().addWidget(self.__mscCtrlValSpin, 9, 1)
        self.__mscCtrlValCheck = QCheckBox(self)
        self.__mscCtrlValCheck.toggled.connect(functools.partial(self.__checked, MscArgument.CTRL_VALUE))
        self.layout().addWidget(self.__mscCtrlValCheck, 9, 2)
        self.__data_widgets[MscArgument.CTRL_VALUE] = [self.__mscCtrlValSpin, self.__mscCtrlValCheck]

        self.__mscTimecodeLabel = QLabel(self)
        self.layout().addWidget(self.__mscTimecodeLabel, 10, 0)
        self.__mscTimecodeEdit = QTimeEdit(self)
        self.__mscTimecodeEdit.setDisplayFormat('HH.mm.ss.zzz')
        self.__mscTimecodeEdit.timeChanged.connect(self.__show_messsage)
        self.layout().addWidget(self.__mscTimecodeEdit, 10, 1)
        self.__mscTimecodeCheck = QCheckBox(self)
        self.__mscTimecodeCheck.toggled.connect(functools.partial(self.__checked, MscArgument.TIMECODE))
        self.layout().addWidget(self.__mscTimecodeCheck, 10, 2)
        self.__data_widgets[MscArgument.TIMECODE] = [self.__mscTimecodeEdit, self.__mscTimecodeCheck]

        self.__mscTimeTypeLabel = QLabel(self)
        self.layout().addWidget(self.__mscTimeTypeLabel, 11, 0)
        self.__mscTimeTypeCombo = QComboBox(self)
        self.__mscTimeTypeCombo.addItems([str(i) for i in MscTimeType])
        self.__mscTimeTypeCombo.setCurrentText(str(MscTimeType.SMPTE))
        self.__mscTimeTypeCombo.currentTextChanged.connect(self.__show_messsage)
        self.layout().addWidget(self.__mscTimeTypeCombo, 11, 1)
        self.__mscTimeTypeCheck = QCheckBox(self)
        self.__mscTimeTypeCheck .toggled.connect(functools.partial(self.__checked, MscArgument.TIME_TYPE))
        self.layout().addWidget(self.__mscTimeTypeCheck, 11, 2)
        self.__data_widgets[MscArgument.TIME_TYPE] = [self.__mscTimeTypeCombo, self.__mscTimeTypeCheck]

        self.__mscPreview = QLabel(self)
        self.__mscPreview.setStyleSheet('font: bold')
        self.__mscPreview.setMinimumHeight(50)
        self.layout().addWidget(self.__mscPreview, 13, 0, 1, 2)

        self.__retranslateUi()

        self.__mscCommandCombo.currentTextChanged.emit(str(MscCommand.GO))

    @property
    def device_id(self):
        return self.__mscDeviceSpin.value()

    @device_id.setter
    def device_id(self, device_id):
        self.__mscDeviceSpin.setValue(device_id)

    @property
    def command_format(self):
        return MscCommandFormat(self.__mscCmdFmtCombo.currentTextChanged())

    @command_format.setter
    def command_format(self, command_format):
        self.__mscCmdFmtCombo.setCurrentText(str(command_format))

    @property
    def command(self):
        return MscCommand(self.__mscCommandCombo.currentText())

    @command.setter
    def command(self, command):
        self.__mscCommandCombo.setCurrentText(str(command))

    def get_argument_widget(self, msc_arg):
        return self.__data_widgets[msc_arg][self.DATA_WIDGET]

    def set_argument(self, msc_arg, arg):
        if msc_arg is MscArgument.TIME_TYPE:
            if not isinstance(arg, MscTimeType):
                raise ValueError("not an MscTimeType")
            self.__data_widgets[msc_arg][self.DATA_WIDGET].setCurrentText(str(arg))
        elif msc_arg is MscArgument.TIMECODE:
            if not isinstance(arg, int) and arg < 0:
                raise ValueError("not an int")
            self.__data_widgets[msc_arg][self.DATA_WIDGET].setTime(QTime().fromMSecsSinceStartOfDay(arg))

        else:
            if not isinstance(arg, (int, float)) and arg < 0:
                raise ValueError("not an int or float")
            self.__data_widgets[msc_arg][self.DATA_WIDGET].setValue(arg)

    def checkbox_enable(self, msc_arg, enable):
        self.__data_widgets[msc_arg][self.CHECK_WIDGET].setEnabled(enable)

    def checkbox_toggle(self, msc_arg, checked):
        self.__data_widgets[msc_arg][self.CHECK_WIDGET].setChecked(checked)

    def __retranslateUi(self):
        self.setTitle(translate('MSCSettings', 'MSC Message'))
        self.__mscDeviceLabel.setText(translate('MSCSettings', 'Device ID'))
        self.__mscCmdFmtLabel.setText(translate('MSCSettings', 'Command Format'))
        self.__mscCommandLabel.setText(translate('MSCSettings', 'MSC Command'))
        self.__mscQNumberLabel.setText(translate('MSCSettings', 'Q_Number'))
        self.__mscQListLabel.setText(translate('MSCSettings', 'Q_List'))
        self.__mscQPathLabel.setText(translate('MSCSettings', 'Q_Path'))
        self.__mscMacroLabel.setText(translate('MSCSettings', 'Macro Number'))
        self.__mscCtrlNumLabel.setText(translate('MSCSettings', 'Generic Control  Number'))
        self.__mscCtrlValLabel.setText(translate('MSCSettings', 'Generic Control  Value'))
        self.__mscTimecodeLabel.setText(translate('MSCSettings', 'Timecode'))

    def get_message(self):
        device_id = self.__mscDeviceSpin.value()
        command = MscCommand(self.__mscCommandCombo.currentText())
        command_format = MscCommandFormat(self.__mscCmdFmtCombo.currentText())

        message = MscMessage(device_id, command_format, command)

        for msc_arg in MscMessage.get_arguments(command):
            if self.__data_widgets[msc_arg][self.CHECK_WIDGET].isChecked():
                if msc_arg is MscArgument.TIME_TYPE:
                    message[msc_arg] = self.__data_widgets[msc_arg][self.DATA_WIDGET].currentText()
                elif msc_arg is MscArgument.TIMECODE:
                    message[msc_arg] = self.__data_widgets[msc_arg][self.DATA_WIDGET].time().msecsSinceStartOfDay()
                else:
                    message[msc_arg] = self.__data_widgets[msc_arg][self.DATA_WIDGET].value()

        return message

    def __show_messsage(self):
        message = self.get_message()
        self.__mscPreview.setText('MSC:  {0}'.format(message.to_hex_str()))

    def __checked(self, msc_arg, checked):
        self.__data_widgets[msc_arg][self.DATA_WIDGET].setEnabled(checked)

        if msc_arg is MscArgument.Q_LIST:
            # self.__data_widgets[MscArgument.Q_PATH][self.CHECK_WIDGET].setChecked(checked)
            self.__data_widgets[MscArgument.Q_PATH][self.CHECK_WIDGET].setEnabled(checked)

        elif msc_arg is MscArgument.Q_PATH:
            self.__data_widgets[MscArgument.Q_LIST][self.CHECK_WIDGET].setEnabled(not checked)

        elif msc_arg is MscArgument.TIMECODE:
            self.__data_widgets[MscArgument.TIME_TYPE][self.CHECK_WIDGET].setChecked(checked)

        elif msc_arg is MscArgument.TIME_TYPE:
            self.__data_widgets[MscArgument.TIME_TYPE][self.CHECK_WIDGET].setEnabled(False)

        self.__show_messsage()

    def __type_changed(self, cmd_str):
        cmd = MscCommand(cmd_str)
        args = MscMessage.get_arguments(cmd)
        for key, widgets in self.__data_widgets.items():
            if key in args:
                if args[key] is cmd:
                    widgets[self.CHECK_WIDGET].setChecked(True)
                    widgets[self.CHECK_WIDGET].setEnabled(False)
                elif key is MscArgument.TIME_TYPE:
                    pass
                else:
                    widgets[self.CHECK_WIDGET].setChecked(True)
                    widgets[self.CHECK_WIDGET].setEnabled(True)
            else:
                widgets[1].setChecked(False)
                widgets[1].setEnabled(False)
                widgets[0].setEnabled(False)
