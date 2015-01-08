##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from PyQt5.QtCore import QTime, QSize
from PyQt5.QtWidgets import *  # @UnusedWildImport

from lisp.application import Application
from lisp.ui.cuelistdialog import CueListDialog
from lisp.ui.settings.section import SettingsSection


class TriggersSettings(SettingsSection):

    Name = 'Triggers'
    Dialog = CueListDialog()

    def __init__(self, size, cue=None, **kwargs):
        super().__init__(size, cue=None, **kwargs)
        self.setLayout(QVBoxLayout(self))

        self.list = QListWidget(self)
        self.list.setAlternatingRowColors(True)
        self.layout().addWidget(self.list)

        self.buttons = QDialogButtonBox(self)
        self.buttons.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.layout().addWidget(self.buttons)

        self.addButton = self.buttons.addButton('Add',
                                                QDialogButtonBox.ActionRole)
        self.delButton = self.buttons.addButton('Remove',
                                                QDialogButtonBox.ActionRole)

        self.addButton.clicked.connect(self._add_trigger_dialog)
        self.delButton.clicked.connect(self._remove_trigger)

        self.Dialog.reset()
        self.Dialog.add_cues(Application().layout.get_cues())

        self.duration = -1

    def _add_new_trigger(self, cue_id, time, name):
        item = QListWidgetItem()
        item.setSizeHint(QSize(200, 30))
        widget = TriggerWidget(item)
        widget.timeEdit.editingFinished.connect(self.list.sortItems)
        widget.load_trigger(cue_id, time, self.duration, name)

        self.list.addItem(item)
        self.list.setItemWidget(item, widget)

    def _add_trigger_dialog(self):
        cue = self.cue_select_dialog()
        if cue is not None:
            self._add_new_trigger(cue['id'], 0, cue['name'])

    def _remove_trigger(self):
        widget = self.list.itemWidget(self.list.item(self.list.currentRow()))
        widget.timeEdit.editingFinished.disconnect()
        self.list.takeItem(self.list.currentRow())

    @classmethod
    def cue_select_dialog(cls):
        if cls.Dialog.exec_() == QDialog.Accepted:
            return cls.Dialog.selected_cues()[0]

    def set_configuration(self, conf):
        if conf is not None:
            self.duration = conf.get('media', {}).get('duration', -1)

            if 'triggers' in conf:
                for position, ids in conf['triggers'].items():
                    for cue_id in ids:
                        cue = Application().layout.get_cue_by_id(cue_id)
                        if cue is not None:
                            self._add_new_trigger(cue_id, position,
                                                  cue['name'])

    def get_configuration(self):
        triggers = {}

        for n in range(self.list.count()):
            trigger = self.list.itemWidget(self.list.item(n))
            position, target = trigger.get_trigger()

            if position not in triggers:
                triggers[position] = [target]
            else:
                triggers[position].append(target)

        return {'triggers': triggers}


class TriggerWidget(QWidget):

    def __init__(self, item, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QHBoxLayout(self))
        self.layout().setContentsMargins(2, 1, 2, 1)

        self.timeEdit = QTimeEdit(self)
        self.timeEdit.timeChanged.connect(self._time_changed)
        self.timeEdit.setDisplayFormat('HH.mm.ss.zzz')
        self.layout().addWidget(self.timeEdit)

        self.nameLabel = QLabel(self)
        self.nameLabel.setStyleSheet('background: rgba(0,0,0,0);'
                                     'padding-left: 2px;')
        self.layout().addWidget(self.nameLabel)

        self.selectButton = QPushButton(self)
        self.selectButton.clicked.connect(self._select_cue)
        self.layout().addWidget(self.selectButton)

        self.layout().setStretch(0, 1)
        self.layout().setStretch(1, 2)
        self.layout().setStretch(2, 1)

        self.retranslateUi()

        self.item = item
        self.cue_id = ''

    def retranslateUi(self):
        self.timeEdit.setToolTip('Minimum step is 100 milliseconds')
        self.selectButton.setText('Select target')

    def load_trigger(self, cue_id, time, duration, name):
        self.cue_id = cue_id
        self.nameLabel.setText(name)
        self.timeEdit.setTime(self._to_qtime(time))

        if duration > 0:
            self.timeEdit.setMaximumTime(self._to_qtime(duration // 100))

    def get_trigger(self):
        return (self._from_qtime(self.timeEdit.time()), self.cue_id)

    def _select_cue(self):
        cue = TriggersSettings.cue_select_dialog()

        if cue is not None:
            self.load_trigger(cue['id'],
                              self._from_qtime(self.timeEdit.time()), -1,
                              cue['name'])

    def _time_changed(self):
        rounded = self._to_qtime(self._from_qtime(self.timeEdit.time()))
        self.timeEdit.setTime(rounded)
        # Set the item text used for sorting
        self.item.setText(rounded.toString(self.timeEdit.displayFormat()))

    def _to_qtime(self, time):
        return QTime.fromMSecsSinceStartOfDay(time * 100)

    def _from_qtime(self, qtime):
        return qtime.msecsSinceStartOfDay() // 100
