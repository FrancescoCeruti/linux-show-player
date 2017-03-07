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

import functools

from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
from PyQt5.QtCore import QTime
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QGridLayout, QLabel, \
    QComboBox, QSpinBox, QDoubleSpinBox, QFrame, QCheckBox, QTimeEdit, QPushButton

from lisp.core.has_properties import Property
from lisp.cues.cue import Cue
from lisp.modules.midi.midi_output import MIDIOutput
from lisp.ui.settings.cue_settings import CueSettingsRegistry
from lisp.ui.settings.settings_page import SettingsPage
from lisp.ui.ui_utils import translate
from lisp.modules.midi.midi_msc import MscMessage, MscCommand, \
    MscCommandFormat, MscArgument, MscStringParser, MscTimeType
from lisp.ui import elogging


class MscCue(Cue):
    Name = QT_TRANSLATE_NOOP('CueName', 'MSC Cue')

    message = Property(default='')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = translate('CueName', self.Name)

        midi_out = MIDIOutput()
        if not midi_out.is_open():
            midi_out.open()

    def __start__(self, fade=False):
        if self.message:
            MIDIOutput().send_from_str(self.message)

        return False


class MscCueSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP('SettingsPageName', 'MSC Settings')

    DATA_WIDGET = 0
    CHECK_WIDGET = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.mscGroup = QGroupBox(self)
        self.mscGroup.setLayout(QGridLayout())
        self.mscGroup.layout().setColumnStretch(0, 10)
        self.mscGroup.layout().setColumnStretch(1, 10)
        self.mscGroup.layout().setColumnStretch(2, 1)
        self.layout().addWidget(self.mscGroup)

        # Device ID
        self.mscDeviceLabel = QLabel(self.mscGroup)
        self.mscGroup.layout().addWidget(self.mscDeviceLabel, 0, 0)
        self.mscDeviceSpin = QSpinBox(self.mscGroup)
        self.mscDeviceSpin.setRange(0, 127)
        self.mscDeviceSpin.setValue(1)
        self.mscDeviceSpin.valueChanged.connect(self.__show_messsage)
        self.mscGroup.layout().addWidget(self.mscDeviceSpin, 0, 1, 1, 2)

        self.mscCmdFmtLabel = QLabel(self.mscGroup)
        self.mscGroup.layout().addWidget(self.mscCmdFmtLabel, 1, 0)
        self.mscCmdFmtCombo = QComboBox(self.mscGroup)
        self.mscCmdFmtCombo.addItems([str(i) for i in MscCommandFormat])
        self.mscCmdFmtCombo.currentTextChanged.connect(self.__show_messsage)
        self.mscGroup.layout().addWidget(self.mscCmdFmtCombo, 1, 1, 1, 2)

        self.mscCommandLabel = QLabel(self.mscGroup)
        self.mscGroup.layout().addWidget(self.mscCommandLabel, 2, 0)
        self.mscCommandCombo = QComboBox(self.mscGroup)
        self.mscCommandCombo.addItems([str(i) for i in MscCommand])
        self.mscCommandCombo.currentTextChanged.connect(self.__type_changed)
        self.mscCommandCombo.currentTextChanged.connect(self.__show_messsage)
        self.mscGroup.layout().addWidget(self.mscCommandCombo, 2, 1, 1, 2)

        line = QFrame(self.mscGroup)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.mscGroup.layout().addWidget(line, 3, 0, 1, 3)

        # Data widgets
        self._data_widgets = {}

        self.mscQNumberLabel = QLabel(self.mscGroup)
        self.mscGroup.layout().addWidget(self.mscQNumberLabel, 4, 0)
        self.mscQNumberSpin = QDoubleSpinBox(self.mscGroup)
        self.mscQNumberSpin.setRange(0, 999)
        self.mscQNumberSpin.setDecimals(3)
        self.mscQNumberSpin.setSingleStep(1.0)
        self.mscQNumberSpin.setValue(1)
        self.mscQNumberSpin.valueChanged.connect(self.__show_messsage)
        self.mscGroup.layout().addWidget(self.mscQNumberSpin, 4, 1)
        self.mscQNumberCheck = QCheckBox(self.mscGroup)
        self.mscQNumberCheck.toggled.connect(functools.partial(self.__checked, MscArgument.Q_NUMBER))
        self.mscGroup.layout().addWidget(self.mscQNumberCheck, 4, 2)
        self._data_widgets[MscArgument.Q_NUMBER] = [self.mscQNumberSpin, self.mscQNumberCheck]

        self.mscQListLabel = QLabel(self.mscGroup)
        self.mscGroup.layout().addWidget(self.mscQListLabel, 5, 0)
        self.mscQListSpin = QDoubleSpinBox(self.mscGroup)
        self.mscQListSpin.setRange(0, 999)
        self.mscQListSpin.setDecimals(3)
        self.mscQListSpin.setSingleStep(1.0)
        self.mscQListSpin.setValue(1)
        self.mscQListSpin.valueChanged.connect(self.__show_messsage)
        self.mscGroup.layout().addWidget(self.mscQListSpin, 5, 1)
        self.mscQListCheck = QCheckBox(self.mscGroup)
        self.mscQListCheck.toggled.connect(functools.partial(self.__checked, MscArgument.Q_LIST))
        self.mscGroup.layout().addWidget(self.mscQListCheck, 5, 2)
        self._data_widgets[MscArgument.Q_LIST] = [self.mscQListSpin, self.mscQListCheck]

        self.mscQPathLabel = QLabel(self.mscGroup)
        self.mscGroup.layout().addWidget(self.mscQPathLabel, 6, 0)
        self.mscQPathSpin = QDoubleSpinBox(self.mscGroup)
        self.mscQPathSpin.setRange(0, 999)
        self.mscQPathSpin.setDecimals(3)
        self.mscQPathSpin.setSingleStep(1.0)
        self.mscQPathSpin.setValue(1)
        self.mscQPathSpin.valueChanged.connect(self.__show_messsage)
        self.mscGroup.layout().addWidget(self.mscQPathSpin, 6, 1)
        self.mscQPathCheck = QCheckBox(self.mscGroup)
        self.mscQPathCheck.toggled.connect(functools.partial(self.__checked, MscArgument.Q_PATH))
        self.mscGroup.layout().addWidget(self.mscQPathCheck, 6, 2)
        self._data_widgets[MscArgument.Q_PATH] = [self.mscQPathSpin, self.mscQPathCheck]

        self.mscMacroLabel = QLabel(self.mscGroup)
        self.mscGroup.layout().addWidget(self.mscMacroLabel, 7, 0)
        self.mscMacroSpin = QSpinBox(self.mscGroup)
        self.mscMacroSpin.setRange(0, 127)
        self.mscMacroSpin.setValue(1)
        self.mscMacroSpin.valueChanged.connect(self.__show_messsage)
        self.mscGroup.layout().addWidget(self.mscMacroSpin, 7, 1)
        self.mscMacroCheck = QCheckBox(self.mscGroup)
        self.mscMacroCheck.toggled.connect(functools.partial(self.__checked, MscArgument.MACRO_NUM))
        self.mscGroup.layout().addWidget(self.mscMacroCheck, 7, 2)
        self._data_widgets[MscArgument.MACRO_NUM] = [self.mscMacroSpin, self.mscMacroCheck]

        self.mscCtrlNumLabel = QLabel(self.mscGroup)
        self.mscGroup.layout().addWidget(self.mscCtrlNumLabel, 8, 0)
        self.mscCtrlNumSpin = QSpinBox(self.mscGroup)
        self.mscCtrlNumSpin.setRange(0, 1023)
        self.mscCtrlNumSpin.setValue(1)
        self.mscCtrlNumSpin.valueChanged.connect(self.__show_messsage)
        self.mscGroup.layout().addWidget(self.mscCtrlNumSpin, 8, 1)
        self.mscCtrlNumCheck = QCheckBox(self.mscGroup)
        self.mscCtrlNumCheck.toggled.connect(functools.partial(self.__checked, MscArgument.CTRL_NUM))
        self.mscGroup.layout().addWidget(self.mscCtrlNumCheck, 8, 2)
        self._data_widgets[MscArgument.CTRL_NUM] = [self.mscCtrlNumSpin, self.mscCtrlNumCheck]

        self.mscCtrlValLabel = QLabel(self.mscGroup)
        self.mscGroup.layout().addWidget(self.mscCtrlValLabel, 9, 0)
        self.mscCtrlValSpin = QSpinBox(self.mscGroup)
        self.mscCtrlValSpin.setRange(0, 1023)
        self.mscCtrlValSpin.setValue(1)
        self.mscCtrlValSpin.valueChanged.connect(self.__show_messsage)
        self.mscGroup.layout().addWidget(self.mscCtrlValSpin, 9, 1)
        self.mscCtrlValCheck = QCheckBox(self.mscGroup)
        self.mscCtrlValCheck.toggled.connect(functools.partial(self.__checked, MscArgument.CTRL_VALUE))
        self.mscGroup.layout().addWidget(self.mscCtrlValCheck, 9, 2)
        self._data_widgets[MscArgument.CTRL_VALUE] = [self.mscCtrlValSpin, self.mscCtrlValCheck]

        self.mscTimecodeLabel = QLabel(self.mscGroup)
        self.mscGroup.layout().addWidget(self.mscTimecodeLabel, 10, 0)
        self.mscTimecodeEdit = QTimeEdit(self.mscGroup)
        self.mscTimecodeEdit.setDisplayFormat('HH.mm.ss.zzz')
        self.mscTimecodeEdit.timeChanged.connect(self.__show_messsage)
        self.mscGroup.layout().addWidget(self.mscTimecodeEdit, 10, 1)
        self.mscTimecodeCheck = QCheckBox(self.mscGroup)
        self.mscTimecodeCheck.toggled.connect(functools.partial(self.__checked, MscArgument.TIMECODE))
        self.mscGroup.layout().addWidget(self.mscTimecodeCheck, 10, 2)
        self._data_widgets[MscArgument.TIMECODE] = [self.mscTimecodeEdit, self.mscTimecodeCheck]

        self.mscTimeTypeLabel = QLabel(self.mscGroup)
        self.mscGroup.layout().addWidget(self.mscTimeTypeLabel, 11, 0)
        self.mscTimeTypeCombo = QComboBox(self.mscGroup)
        self.mscTimeTypeCombo.addItems([str(i) for i in MscTimeType])
        self.mscTimeTypeCombo.currentTextChanged.connect(self.__show_messsage)
        self.mscGroup.layout().addWidget(self.mscTimeTypeCombo, 11, 1)
        self.mscTimeTypeCheck = QCheckBox(self.mscGroup)
        self.mscTimeTypeCheck .toggled.connect(functools.partial(self.__checked, MscArgument.TIME_TYPE))
        self.mscGroup.layout().addWidget(self.mscTimeTypeCheck, 11, 2)
        self._data_widgets[MscArgument.TIME_TYPE] = [self.mscTimeTypeCombo, self.mscTimeTypeCheck]

        self.mscPreview = QLabel(self.mscGroup)
        self.mscPreview.setStyleSheet('font: bold')
        self.mscPreview.setMinimumHeight(50)
        self.mscGroup.layout().addWidget(self.mscPreview, 13, 0, 1, 2)

        self.testButton = QPushButton(self.mscGroup)
        self.testButton.pressed.connect(self.__test_message)
        self.mscGroup.layout().addWidget(self.testButton, 13, 2)

        self.retranslateUi()

        self.mscCommandCombo.currentTextChanged.emit(str(MscCommand.GO))

    def retranslateUi(self):
        self.mscGroup.setTitle(translate('MSCCue', 'MSC Message'))
        self.mscDeviceLabel.setText(translate('MSCCue', 'Device ID'))
        self.mscCmdFmtLabel.setText(translate('MSCCue', 'Command Format'))
        self.mscCommandLabel.setText(translate('MSCCue', 'MSC Command'))
        self.mscQNumberLabel.setText(translate('MSCCue', 'Q_Number'))
        self.mscQListLabel.setText(translate('MSCCue', 'Q_List'))
        self.mscQPathLabel.setText(translate('MSCCue', 'Q_Path'))
        self.mscMacroLabel.setText(translate('MSCCue', 'Macro Number'))
        self.mscCtrlNumLabel.setText(translate('MSCCue', 'Generic Control  Number'))
        self.mscCtrlValLabel.setText(translate('MSCCue', 'Generic Control  Value'))
        self.mscTimecodeLabel.setText(translate('MSCCue', 'Timecode'))
        self.testButton.setText(translate('MSCCue', 'Test'))


    def __get_message(self):
        device_id = self.mscDeviceSpin.value()
        command = MscCommand(self.mscCommandCombo.currentText())
        command_format = MscCommandFormat(self.mscCmdFmtCombo.currentText())

        message = MscMessage(device_id, command_format, command)

        for msc_arg in MscMessage.get_arguments(command):
            if self._data_widgets[msc_arg][self.CHECK_WIDGET].isChecked():
                if msc_arg is MscArgument.TIME_TYPE:
                    message[msc_arg] = self._data_widgets[msc_arg][self.DATA_WIDGET].currentText()
                elif msc_arg is MscArgument.TIMECODE:
                    message[msc_arg] = self._data_widgets[msc_arg][self.DATA_WIDGET].time().msecsSinceStartOfDay()
                else:
                    message[msc_arg] = self._data_widgets[msc_arg][self.DATA_WIDGET].value()

        return message

    def __test_message(self):
        message = self.__get_message()
        MIDIOutput().send_from_str(message.message_str)

    def __show_messsage(self):
        message = self.__get_message()
        self.mscPreview.setText('MSC:  {0}'.format(message.to_hex_str()))

    def __checked(self, msc_arg, checked):
        self._data_widgets[msc_arg][self.DATA_WIDGET].setEnabled(checked)

        if msc_arg is MscArgument.Q_LIST:
            self._data_widgets[MscArgument.Q_PATH][self.CHECK_WIDGET].setChecked(checked)
            self._data_widgets[MscArgument.Q_PATH][self.CHECK_WIDGET].setEnabled(checked)

        elif msc_arg is MscArgument.Q_PATH:
            self._data_widgets[MscArgument.Q_LIST][self.CHECK_WIDGET].setEnabled(not checked)

        elif msc_arg is MscArgument.TIMECODE:
            self._data_widgets[MscArgument.TIME_TYPE][self.CHECK_WIDGET].setChecked(checked)

        elif msc_arg is MscArgument.TIME_TYPE:
            self._data_widgets[MscArgument.TIME_TYPE][self.CHECK_WIDGET].setEnabled(False)

        self.__show_messsage()

    def __type_changed(self, cmd_str):
        cmd = MscCommand(cmd_str)
        args = MscMessage.get_arguments(cmd)
        for key, widgets in self._data_widgets.items():
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

    def get_settings(self):

        message = self.__get_message()
        msg_str = message.message_str
        if not msg_str:
            elogging.error("MscCue: could not create MSC messsage")

        elogging.debug("MscCue: message string: {0}".format(msg_str))
        return {'message': msg_str}

    def load_settings(self, settings):
        msg_str = settings.get('message', '')

        if not msg_str:
            return

        print(msg_str)
        parser = MscStringParser(msg_str)

        if not parser.valid:
            elogging.error("MscCue: could not parse MSC message")
            return

        self.mscDeviceSpin.setValue(parser.device_id)
        self.mscCommandCombo.setCurrentText(str(parser.command))
        self.mscCmdFmtCombo.setCurrentText(str(parser.command_format))

        for msc_arg in MscArgument:
            value = parser.get(msc_arg)
            if value is not None:
                if msc_arg is MscArgument.TIME_TYPE:
                    pass
                elif msc_arg is MscArgument.TIMECODE:
                    self.mscTimeTypeCombo.setCurrentText(str(parser[MscArgument.TIME_TYPE]))
                    self.mscTimecodeEdit.setTime(QTime().fromMSecsSinceStartOfDay(value))
                    self._data_widgets[msc_arg][self.CHECK_WIDGET].setChecked(True)
                    self._data_widgets[msc_arg][self.CHECK_WIDGET].setEnabled(not parser.required(msc_arg))
                else:
                    self._data_widgets[msc_arg][self.DATA_WIDGET].setValue(value)
                    self._data_widgets[msc_arg][self.CHECK_WIDGET].setChecked(True)
                    self._data_widgets[msc_arg][self.CHECK_WIDGET].setEnabled(not parser.required(msc_arg))

            else:
                self._data_widgets[msc_arg][self.CHECK_WIDGET].setChecked(False)


CueSettingsRegistry().add_item(MscCueSettings, MscCue)
