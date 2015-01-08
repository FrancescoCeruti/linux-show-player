##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from copy import deepcopy
from operator import itemgetter

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *  # @UnusedWildImport
from lisp.gst import elements
from lisp.utils.audio_utils import db_to_linear, linear_to_db

from lisp.gst.elements.sink_selector import SinkSelector
from lisp.ui.qmutebutton import QMuteButton
from lisp.ui.settings.section import SettingsSection


class SettingsDialog(QDialog):

    def __init__(self, section, conf, **kwds):
        super().__init__(**kwds)
        self.setWindowModality(Qt.ApplicationModal)
        self.setLayout(QVBoxLayout(self))

        self.settings = section(None, 'sink', parent=self)
        self.settings.set_configuration({'sink': conf})
        self.layout().addWidget(self.settings)

        self.buttons = QDialogButtonBox(self)
        self.buttons.setStandardButtons(QDialogButtonBox.Ok |
                                        QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout().addWidget(self.buttons)

        self.resize(self.settings.width() + 20,
                    self.settings.height() + 75)

    def get_settings(self):
        return self.settings.get_configuration().get('sink', {})


class OutputWidget(QWidget):

    Sections = {}

    def __init__(self, conf, parent=None):
        super().__init__(parent)

        # Import here for avoid circular import
        if len(self.Sections) == 0:
            from lisp.gst import settings
            OutputWidget.Sections = settings.sections_by_element_name()

        self._conf = conf

        self.gridLayout = QGridLayout(self)

        self.outputType = QLabel(self)
        self.outputType.setAlignment(Qt.AlignCenter)
        self.outputType.setText(conf['name'])
        self.gridLayout.addWidget(self.outputType, 0, 0, 1, 2)

        self.sinkSettings = QPushButton('Settings', self)
        self.sinkSettings.setEnabled(self._conf['name'] in self.Sections)
        self.sinkSettings.setIcon(QIcon.fromTheme('settings'))
        self.gridLayout.addWidget(self.sinkSettings, 0, 2)

        self.mute = QMuteButton(self)
        self.mute.setMute(conf.get('mute', False))
        self.gridLayout.addWidget(self.mute, 1, 0)

        self.volume = QSlider(Qt.Horizontal, self)
        self.volume.setRange(-100, 0)
        self.volume.setPageStep(1)
        volume = linear_to_db(conf.get('volume', 1))
        self.volume.setValue(volume)
        self.gridLayout.addWidget(self.volume, 1, 1)

        self.volumeLabel = QLabel(self)
        self.volumeLabel.setText(str(volume) + ' dB')
        self.volumeLabel.setAlignment(Qt.AlignCenter)
        self.gridLayout.addWidget(self.volumeLabel, 1, 2)

        self.volume.valueChanged.connect(self._volume_changed)
        self.sinkSettings.clicked.connect(self._settings)

    def get_settings(self):
        self._conf['volume'] = db_to_linear(self.volume.value())
        self._conf['mute'] = self.mute.isMute()

        return self._conf

    def _volume_changed(self, value):
        self.volumeLabel.setText(str(value) + ' dB')

    def _settings(self):
        dialog = SettingsDialog(self.Sections[self._conf['name']], self._conf)
        dialog.exec_()

        if dialog.result() == dialog.Accepted:
            self._conf.update(dialog.get_settings())


class SinkSelectorSettings(SettingsSection):

    NAME = 'Multi-Sink Selector'
    ELEMENT = SinkSelector

    Sinks = elements.outputs()

    def __init__(self, size, Id, parent=None):
        super().__init__(size, parent)

        self.id = Id
        self._sinks = []

        self.groupBox = QGroupBox(self)
        self.groupBox.setTitle('Add/Remove outputs')
        self.groupBox.resize(self.width(), self.height())

        self.vlayout = QVBoxLayout(self.groupBox)
        self.vlayout.setContentsMargins(0, 5, 0, 0)

        self.sinksList = QListWidget(self.groupBox)
        self.sinksList.setAlternatingRowColors(True)
        self.vlayout.addWidget(self.sinksList)

        self.buttons = QDialogButtonBox(self.groupBox)
        self.vlayout.addWidget(self.buttons)

        self.add = QPushButton('Add')
        self.remove = QPushButton('Remove')
        self.buttons.addButton(self.add, QDialogButtonBox.YesRole)
        self.buttons.addButton(self.remove, QDialogButtonBox.NoRole)

        self.vlayout.activate()

        self.add.clicked.connect(self._new_sink)
        self.remove.clicked.connect(self.__remove_sink)

    def set_configuration(self, conf):
        if conf is not None and self.id in conf:
            conf = deepcopy(conf)
            for key in conf[self.id]:
                self.__add_sink(conf[self.id][key], key)
        else:
            self.__add_sink({'name': 'AutoSink'}, 'sink0')

    def get_configuration(self):
        conf = {}

        if not (self.groupBox.isCheckable() and not self.groupBox.isChecked()):
            conf[self.id] = {}
            for widget, name in self._sinks:
                conf[self.id][name] = widget.get_settings()

        return conf

    def enable_check(self, enable):
        self.groupBox.setCheckable(enable)
        self.groupBox.setChecked(False)

    def _new_sink(self):
        sinks = sorted(self.Sinks.keys())
        sinks.remove('SinkSelector')
        name, ok = QInputDialog.getItem(self, "Output", "Select output device",
                                        sinks, editable=False)
        if ok:
            self.__add_sink({'name': name})

    def __new_name(self):
        suff = 0

        for _, name in sorted(self._sinks, key=itemgetter(1)):
            if 'sink' + str(suff) != name:
                break
            suff += 1

        return 'sink' + str(suff)

    def __add_sink(self, properties, name=None):
        widget = OutputWidget(properties, self.sinksList)
        widget.resize(self.sinksList.width() - 5, 80)

        item = QListWidgetItem()
        item.setSizeHint(widget.size())

        if name is None:
            name = self.__new_name()

        self._sinks.append((widget, name))
        self.sinksList.addItem(item)
        self.sinksList.setItemWidget(item, widget)

        self.remove.setEnabled(len(self._sinks) > 1)

    def __remove_sink(self):
        self._sinks.pop(self.sinksList.currentRow())
        self.sinksList.removeItemWidget(self.sinksList.currentItem())
        self.sinksList.takeItem(self.sinksList.currentRow())

        self.remove.setEnabled(len(self._sinks) > 1)
