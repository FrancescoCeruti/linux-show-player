# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2015 Francesco Ceruti <ceppofrancy@gmail.com>
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

from copy import deepcopy

from PyQt5.QtWidgets import QGridLayout, QListWidget, QPushButton, \
    QStackedWidget, QListWidgetItem

from lisp.backends.gst.gst_pipe_edit import GstPipeEdit
from lisp.backends.gst.settings import sections_by_element_name
from lisp.ui.settings.section import SettingsSection


class GstMediaSettings(SettingsSection):

    Name = 'Media Settings'

    def __init__(self, size, cue=None, parent=None):
        super().__init__(size, cue=cue, parent=parent)
        self._pipe = ()
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
        if conf is not None:
            conf = conf.get('_media_', {})

            # Activate the layout, so we can get the right widgets size
            self.glayout.activate()

            # Create a local copy of the configuration
            self._conf = deepcopy(conf)

            # Create the widgets
            sections = sections_by_element_name()
            for element in conf.get('pipe', ()):
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

        return {'_media_': conf}

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
        self._conf.update(self.get_configuration()['_media_'])

        # Show the dialog
        dialog = GstPipeEdit(self._conf.get('pipe', ()), parent=self)

        if dialog.exec_() == dialog.Accepted:
            # Reset the view
            for _ in range(self.elements.count()):
                self.elements.removeWidget(self.elements.widget(0))
            self.listWidget.clear()

            # Reload with the new pipeline
            self._conf['pipe'] = dialog.get_pipe()

            self.set_configuration({'_media_': self._conf})
            self.enable_check(self._check)
