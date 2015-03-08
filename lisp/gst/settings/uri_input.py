##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

import os.path

from PyQt5.QtCore import QStandardPaths, Qt
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QPushButton, QLineEdit, \
    QGridLayout, QCheckBox, QSpinBox, QLabel, QFileDialog
from lisp.ui.mainwindow import MainWindow
from lisp.utils.configuration import config

from lisp.gst.elements.uri_input import UriInput
from lisp.ui.settings.section import SettingsSection
from lisp.utils.util import gst_file_extensions, file_filters_from_exts


class UriInputSettings(SettingsSection):

    NAME = 'URI Input'
    ELEMENT = UriInput

    def __init__(self, size, Id, parent=None):
        super().__init__(size, parent)

        self.id = Id

        self.groupFile = QGroupBox('Source', self)
        self.groupFile.setGeometry(0, 0, self.width(), 80)

        self.horizontalLayout = QHBoxLayout(self.groupFile)

        self.buttonFindFile = QPushButton(self.groupFile)
        self.buttonFindFile.setText('Find file')
        self.horizontalLayout.addWidget(self.buttonFindFile)

        self.filePath = QLineEdit('file://', self.groupFile)
        self.horizontalLayout.addWidget(self.filePath)

        self.groupBuffering = QGroupBox('Buffering', self)
        self.groupBuffering.setGeometry(0, 90, self.width(), 120)

        self.bufferingLayout = QGridLayout(self.groupBuffering)

        self.useBuffering = QCheckBox('Use buffering', self.groupBuffering)
        self.bufferingLayout.addWidget(self.useBuffering, 0, 0, 1, 2)

        self.download = QCheckBox(self.groupBuffering)
        self.download.setText('Attempt download on network streams')
        self.bufferingLayout.addWidget(self.download, 1, 0, 1, 2)

        self.bufferSize = QSpinBox(self.groupBuffering)
        self.bufferSize.setRange(-1, 2147483647)
        self.bufferSize.setValue(-1)
        self.bufferingLayout.addWidget(self.bufferSize, 2, 0)

        self.bufferSizeLabel = QLabel(self.groupBuffering)
        self.bufferSizeLabel.setText('Buffer size (-1 default value)')
        self.bufferSizeLabel.setAlignment(Qt.AlignCenter)
        self.bufferingLayout.addWidget(self.bufferSizeLabel, 2, 1)

        self.buttonFindFile.clicked.connect(self.select_file)

    def get_configuration(self):
        conf = {self.id: {}}

        checkable = self.groupFile.isCheckable()

        if not (checkable and not self.groupFile.isChecked()):
            conf[self.id]['uri'] = self.filePath.text()
        if not (checkable and not self.groupBuffering.isChecked()):
            conf[self.id]['use-buffing'] = self.useBuffering.isChecked()
            conf[self.id]['download'] = self.download.isChecked()
            conf[self.id]['buffer-size'] = self.bufferSize.value()

        return conf

    def set_configuration(self, conf):
        if conf is not None and self.id in conf:
            self.filePath.setText(conf[self.id]['uri'])

    def enable_check(self, enable):
        self.groupFile.setCheckable(enable)
        self.groupFile.setChecked(False)

    def select_file(self):
        path = QStandardPaths.writableLocation(QStandardPaths.MusicLocation)
        file = QFileDialog.getOpenFileName(self, 'Choose file', path,
                                           UriInputSettings.exts())[0]

        if file != '':
            self.filePath.setText('file://' + file)

    @classmethod
    def initialize(cls):
        MainWindow().register_cue_options_ui('Media cue (from file)',
                                             cls._gstmediacue_file_dialog,
                                             category='Media cues',
                                             shortcut='CTRL+M')

    @staticmethod
    def exts():
        exts = gst_file_extensions(['audio', 'video'])
        exts = file_filters_from_exts({'Audio files': exts.pop('audio'),
                                       'Video files': exts.pop('video')})
        return exts

    # Function to be registered in the mainWindow
    @staticmethod
    def _gstmediacue_file_dialog():
        path = QStandardPaths.writableLocation(QStandardPaths.MusicLocation)

        files, _ = QFileDialog.getOpenFileNames(MainWindow(), 'Choose files',
                                                path, UriInputSettings.exts())

        options = []
        pipe = 'URIInput!' + config['Gst']['Pipeline']

        for file in files:
            elements = {'URIInput': {'uri': 'file://' + file}}
            options.append({'media': {'pipe': pipe, 'elements': elements},
                            'type': config['Gst']['CueType'],
                            'name': os.path.basename(file)})

        return options
