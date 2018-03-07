# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2018 Francesco Ceruti <ceppofrancy@gmail.com>
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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QToolBar, \
    QMainWindow, QStatusBar, QLabel, QTableView, QToolButton

from lisp.ui.logging.common import LOG_LEVELS, LogAttributeRole, LOG_ATTRIBUTES
from lisp.ui.logging.models import LogRecordFilterModel
from lisp.ui.ui_utils import translate


class LogViewer(QMainWindow):
    """Provide a custom window to display a simple list of logging records.

    Displayed records can be filtered based on their level.
    """

    def __init__(self, log_model, config, **kwargs):
        """
        :type log_model: lisp.ui.logging.models.LogRecordModel
        :type config: lisp.core.configuration.Configuration
        """
        super().__init__(**kwargs)
        self.resize(700, 500)
        self.setWindowTitle(
            translate('Logging', 'Linux Show Player - Log Viewer'))
        self.setStatusBar(QStatusBar(self))

        # Add a permanent label to the toolbar to display shown/filter records
        self.statusLabel = QLabel()
        self.statusBar().addPermanentWidget(self.statusLabel)

        # ToolBar
        self.optionsToolBar = QToolBar(self)
        self.addToolBar(self.optionsToolBar)
        # Create level-toggle actions
        self.levelsActions = self._create_actions(
            self.optionsToolBar, LOG_LEVELS, self._toggle_level)

        self.columnsMenu = QToolButton()
        self.columnsMenu.setText('Columns')
        self.columnsMenu.setPopupMode(QToolButton.InstantPopup)
        # Create column-toggle actions
        self.columnsActions = self._create_actions(
            self.columnsMenu, LOG_ATTRIBUTES, self._toggle_column)

        self.optionsToolBar.addSeparator()
        self.optionsToolBar.addWidget(self.columnsMenu)

        # Setup level filters and columns
        visible_levels = config.get('logging.viewer.visibleLevels', ())
        visible_columns = config.get('logging.viewer.visibleColumns', ())
        for level in visible_levels:
            self.levelsActions[level].setChecked(True)

        # Filter model to show/hide records based on their level
        self.filterModel = LogRecordFilterModel(visible_levels)
        self.filterModel.setSourceModel(log_model)

        # List view to display the messages stored in the model
        self.logView = QTableView(self)
        self.logView.setModel(self.filterModel)
        self.logView.setSelectionMode(QTableView.NoSelection)
        self.logView.setFocusPolicy(Qt.NoFocus)
        self.setCentralWidget(self.logView)

        # Setup visible columns
        for n in range(self.filterModel.columnCount()):
            column = self.filterModel.headerData(
                n, Qt.Horizontal, LogAttributeRole)
            visible = column in visible_columns

            self.columnsActions[column].setChecked(visible)
            self.logView.setColumnHidden(n, not visible)

        # When the filter model change, update the status-label
        self.filterModel.rowsInserted.connect(self._rows_changed)
        self.filterModel.rowsRemoved.connect(self._rows_changed)
        self.filterModel.modelReset.connect(self._rows_changed)

    def _rows_changed(self, *args):
        self.statusLabel.setText(
            'Showing {} of {} records'.format(
                self.filterModel.rowCount(),
                self.filterModel.sourceModel().rowCount())
        )
        self.logView.resizeColumnsToContents()
        self.logView.scrollToBottom()

    def _create_actions(self, menu, actions, trigger_slot):
        menu_actions = {}
        for key, name in actions.items():
            action = QAction(translate('Logging', name))
            action.setCheckable(True)
            action.triggered.connect(self._action_slot(trigger_slot, key))

            menu.addAction(action)
            menu_actions[key] = action

        return menu_actions

    @staticmethod
    def _action_slot(target, attr):
        def slot(checked):
            target(attr, checked)

        return slot

    def _toggle_level(self, level, toggle):
        if toggle:
            self.filterModel.showLevel(level)
        else:
            self.filterModel.hideLevel(level)

    def _toggle_column(self, column, toggle):
        for n in range(self.filterModel.columnCount()):
            column_n = self.filterModel.headerData(
                n, Qt.Horizontal, LogAttributeRole)

            if column_n == column:
                self.logView.setColumnHidden(n, not toggle)
                self.logView.resizeColumnsToContents()
                return
