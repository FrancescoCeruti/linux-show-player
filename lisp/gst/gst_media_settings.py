##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from copy import deepcopy

from PyQt5.QtWidgets import *  # @UnusedWildImport

from lisp.gst.gst_pipe_edit import GstPipeEdit
from lisp.gst.settings import sections_by_element_name
from lisp.ui.settings.section import SettingsSection


class GstMediaSettings(SettingsSection):

    Name = 'Media Settings'

    def __init__(self, size, cue=None, parent=None):
        super().__init__(size, cue=cue, parent=parent)
        self._pipe = ''
        self._conf = {}
        self._check = False

        self.glayout = QGridLayout(self)

        self.listWidget = QListWidget(self)
        self.glayout.addWidget(self.listWidget, 0, 0)

        self.pipeButton = QPushButton('Change Pipe', self)
        self.glayout.addWidget(self.pipeButton, 1, 0)

        self.elements = QStackedWidget(self)
        self.glayout.addWidget(self.elements, 0, 1, 2, 1)

        self.glayout.setColumnStretch(0, 2)
        self.glayout.setColumnStretch(1, 5)

        self.listWidget.currentItemChanged.connect(self.__change_page)
        self.pipeButton.clicked.connect(self.__edit_pipe)

    def set_configuration(self, conf):
        # Get the media section of the cue configuration
        if conf is not None:
            conf = conf.get('media', {})

            # Activate the layout, so we can get the right widgets size
            self.glayout.activate()

            # Create a local copy of the configuration
            self._conf = deepcopy(conf)

            # Create the widgets
            sections = sections_by_element_name()
            for element in conf.get('pipe', '').split('!'):
                widget = sections.get(element)

                if widget is not None:
                    widget = widget(self.elements.size(), element, self)
                    widget.set_configuration(self._conf['elements'])
                    self.elements.addWidget(widget)

                    item = QListWidgetItem(widget.NAME)
                    self.listWidget.addItem(item)

            self.listWidget.setCurrentRow(0)

    def get_configuration(self):
        conf = {'elements': {}}

        for el in self.elements.children():
            if isinstance(el, SettingsSection):
                conf['elements'].update(el.get_configuration())

        # If in check mode the pipeline is not returned
        if not self._check:
            conf['pipe'] = self._conf['pipe']

        return {'media': conf}

    def enable_check(self, enable):
        self._check = enable
        for element in self.elements.children():
            if isinstance(element, SettingsSection):
                element.enable_check(enable)

    def __change_page(self, current, previous):
        if not current:
            current = previous

        self.elements.setCurrentIndex(self.listWidget.row(current))

    def __edit_pipe(self):
        # Backup the settings
        self._conf.update(self.get_configuration()['media'])

        # Show the dialog
        dialog = GstPipeEdit(self._conf.get('pipe', ''), parent=self)

        if dialog.exec_() == dialog.Accepted:
            # Reset the view
            for _ in range(self.elements.count()):
                self.elements.removeWidget(self.elements.widget(0))
            self.listWidget.clear()

            # Reload with the new pipeline
            self._conf['pipe'] = dialog.get_pipe()

            self.set_configuration({'media': self._conf})
            self.enable_check(self._check)
