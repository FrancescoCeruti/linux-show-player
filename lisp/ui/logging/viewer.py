# This file is part of Linux Show Player
#
# Copyright 2018 Francesco Ceruti <ceppofrancy@gmail.com>
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
from PyQt5.QtWidgets import (
    QAction,
    QToolBar,
    QMainWindow,
    QStatusBar,
    QLabel,
    QTableView,
    QVBoxLayout,
    QWidget,
    QSplitter,
)

from lisp.ui.icons import IconTheme
from lisp.ui.logging.common import (
    LOG_LEVELS,
    LogAttributeRole,
    LOG_ICONS_NAMES,
    LogRecordRole,
)
from lisp.ui.logging.details import LogDetails
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
        self.setWindowTitle(
            translate("Logging", "Linux Show Player - Log Viewer")
        )
        self.resize(800, 600)
        self.setCentralWidget(QSplitter())
        self.centralWidget().setOrientation(Qt.Vertical)
        self.setStatusBar(QStatusBar(self))

        # Add a permanent label to the toolbar to display shown/filter records
        self.statusLabel = QLabel()
        self.statusBar().addPermanentWidget(self.statusLabel)

        # ToolBar
        self.optionsToolBar = QToolBar(self)
        self.optionsToolBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.addToolBar(self.optionsToolBar)
        # Create level-toggle actions
        self.levelsActions = self._createActions(
            self.optionsToolBar, LOG_LEVELS, LOG_ICONS_NAMES, self._toggleLevel
        )

        # Setup level filters and columns
        visible_levels = config.get("logging.viewer.visibleLevels", ())
        visible_columns = config.get("logging.viewer.visibleColumns", ())
        for level in visible_levels:
            self.levelsActions[level].setChecked(True)

        # Filter model to show/hide records based on their level
        self.filterModel = LogRecordFilterModel(visible_levels)
        self.filterModel.setSourceModel(log_model)

        # View to display the messages stored in the model
        self.logView = QTableView(self)
        self.logView.setModel(self.filterModel)
        self.logView.setSelectionMode(QTableView.SingleSelection)
        self.logView.setSelectionBehavior(QTableView.SelectRows)
        self.logView.horizontalHeader().setStretchLastSection(True)
        self.centralWidget().addWidget(self.logView)

        # Display selected entry details
        self.detailsView = LogDetails(self)
        self.centralWidget().addWidget(self.detailsView)

        self.centralWidget().setStretchFactor(0, 3)
        self.centralWidget().setStretchFactor(1, 2)

        # Setup visible columns
        for n in range(self.filterModel.columnCount()):
            column = self.filterModel.headerData(
                n, Qt.Horizontal, LogAttributeRole
            )

            self.logView.setColumnHidden(n, not column in visible_columns)

        # When the filter model change, update the status-label
        self.filterModel.rowsInserted.connect(self._rowsChanged)
        self.filterModel.rowsRemoved.connect(self._rowsChanged)
        self.filterModel.modelReset.connect(self._rowsChanged)

        self.logView.selectionModel().selectionChanged.connect(
            self._selectionChanged
        )

    def _selectionChanged(self, selection):
        if selection.indexes():
            self.detailsView.setLogRecord(
                self.filterModel.data(selection.indexes()[0], LogRecordRole)
            )
        else:
            self.detailsView.setLogRecord(None)

    def _rowsChanged(self):
        self.statusLabel.setText(
            "Showing {} of {} records".format(
                self.filterModel.rowCount(),
                self.filterModel.sourceModel().rowCount(),
            )
        )
        self.logView.resizeColumnsToContents()
        # QT Misbehavior: we need to reset the flag
        self.logView.horizontalHeader().setStretchLastSection(False)
        self.logView.horizontalHeader().setStretchLastSection(True)

        self.logView.scrollToBottom()
        # Select the last row (works also if the index is invalid)
        self.logView.setCurrentIndex(
            self.filterModel.index(self.filterModel.rowCount() - 1, 0)
        )

    def _createActions(self, menu, actions, icons, trigger_slot):
        menu_actions = {}
        for key, name in actions.items():
            action = QAction(
                IconTheme.get(icons.get(key)), translate("Logging", name)
            )
            action.setCheckable(True)
            action.triggered.connect(self._actionSlot(trigger_slot, key))

            menu.addAction(action)
            menu_actions[key] = action

        return menu_actions

    @staticmethod
    def _actionSlot(target, attr):
        def slot(checked):
            target(attr, checked)

        return slot

    def _toggleLevel(self, level, toggle):
        if toggle:
            self.filterModel.showLevel(level)
        else:
            self.filterModel.hideLevel(level)
