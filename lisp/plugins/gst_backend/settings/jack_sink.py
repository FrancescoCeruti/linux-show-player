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

import jack
import logging
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPolygon, QPainterPath
from PyQt5.QtWidgets import (
    QGroupBox,
    QWidget,
    QHBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QGridLayout,
    QDialog,
    QDialogButtonBox,
    QPushButton,
    QVBoxLayout,
)

from lisp.plugins.gst_backend.elements.jack_sink import JackSink
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


logger = logging.getLogger(__name__)


class JackSinkSettings(SettingsPage):
    ELEMENT = JackSink
    Name = ELEMENT.Name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.jackGroup = QGroupBox(self)
        self.jackGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.jackGroup)

        self.connectionsEdit = QPushButton(self.jackGroup)
        self.connectionsEdit.clicked.connect(self.__edit_connections)
        self.jackGroup.layout().addWidget(self.connectionsEdit)

        self.__jack_client = None
        try:
            self.__jack_client = jack.Client(
                "LinuxShowPlayer_SettingsControl", no_start_server=True
            )
        except jack.JackError:
            # Disable the widget
            self.setEnabled(False)
            logger.error(
                "Cannot connect with a running Jack server.", exc_info=True
            )

        # if __jack_client is None this will return a default value
        self.connections = JackSink.default_connections(self.__jack_client)

        self.retranlsateUi()

    def retranlsateUi(self):
        self.jackGroup.setTitle(translate("JackSinkSettings", "Connections"))
        self.connectionsEdit.setText(
            translate("JackSinkSettings", "Edit connections")
        )

    def closeEvent(self, event):
        if self.__jack_client is not None:
            self.__jack_client.close()
        super().closeEvent(event)

    def getSettings(self):
        settings = {}

        if not (
            self.jackGroup.isCheckable() and not self.jackGroup.isChecked()
        ):
            settings["connections"] = self.connections

        return settings

    def loadSettings(self, settings):
        connections = settings.get("connections", [])
        if connections:
            self.connections = connections.copy()

    def enableCheck(self, enabled):
        self.jackGroup.setCheckable(enabled)
        self.jackGroup.setChecked(False)

    def __edit_connections(self):
        dialog = JackConnectionsDialog(self.__jack_client, parent=self)
        dialog.set_connections(self.connections.copy())
        dialog.exec()

        if dialog.result() == dialog.Accepted:
            self.connections = dialog.connections


class ClientItem(QTreeWidgetItem):
    def __init__(self, client_name):
        super().__init__([client_name])

        self.name = client_name
        self.ports = {}

    def add_port(self, port_name):
        port = PortItem(port_name)

        self.addChild(port)
        self.ports[port_name] = port


class PortItem(QTreeWidgetItem):
    def __init__(self, port_name):
        super().__init__([port_name[: port_name.index(":")]])

        self.name = port_name


class ConnectionsWidget(QWidget):
    """Code ported from QJackCtl (http://qjackctl.sourceforge.net)"""

    def __init__(self, output_widget, input_widget, parent=None, **kwargs):
        super().__init__(parent)

        self._output_widget = output_widget
        self._input_widget = input_widget
        self.connections = []

    def paintEvent(self, QPaintEvent):
        yc = self.y()
        yo = self._output_widget.y()
        yi = self._input_widget.y()

        x1 = 0
        x2 = self.width()
        h1 = self._output_widget.header().sizeHint().height()
        h2 = self._input_widget.header().sizeHint().height()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for output, out_conn in enumerate(self.connections):
            y1 = int(
                self.item_y(self._output_widget.topLevelItem(output))
                + (yo - yc)
            )

            for client in range(self._input_widget.topLevelItemCount()):
                client = self._input_widget.topLevelItem(client)

                for port in client.ports:
                    if port in self.connections[output]:
                        y2 = int(self.item_y(client.ports[port]) + (yi - yc))
                        self.draw_connection_line(
                            painter, x1, y1, x2, y2, h1, h2
                        )

        painter.end()

    @staticmethod
    def draw_connection_line(painter, x1, y1, x2, y2, h1, h2):
        # Account for list view headers.
        y1 += h1
        y2 += h2

        # Invisible output ports don't get a connecting dot.
        if y1 > h1:
            painter.drawLine(x1, y1, x1 + 4, y1)

        # Setup control points
        spline = QPolygon(4)
        cp = int((x2 - x1 - 8) * 0.4)
        spline.setPoints(
            x1 + 4, y1, x1 + 4 + cp, y1, x2 - 4 - cp, y2, x2 - 4, y2
        )
        # The connection line
        path = QPainterPath()
        path.moveTo(spline.at(0))
        path.cubicTo(spline.at(1), spline.at(2), spline.at(3))
        painter.strokePath(path, painter.pen())

        # painter.drawLine(x1 + 4, y1, x2 - 4, y2)

        # Invisible input ports don't get a connecting dot.
        if y2 > h2:
            painter.drawLine(x2 - 4, y2, x2, y2)

    @staticmethod
    def item_y(item):
        tree_widget = item.treeWidget()
        parent = item.parent()

        if parent is not None and not parent.isExpanded():
            rect = tree_widget.visualItemRect(parent)
        else:
            rect = tree_widget.visualItemRect(item)

        return rect.top() + rect.height() / 2


class JackConnectionsDialog(QDialog):
    def __init__(self, jack_client, parent=None, **kwargs):
        super().__init__(parent)

        self.resize(600, 400)

        self.setLayout(QGridLayout())

        self.output_widget = QTreeWidget(self)
        self.input_widget = QTreeWidget(self)

        self.connections_widget = ConnectionsWidget(
            self.output_widget, self.input_widget, parent=self
        )
        self.output_widget.itemExpanded.connect(self.connections_widget.update)
        self.output_widget.itemCollapsed.connect(self.connections_widget.update)
        self.input_widget.itemExpanded.connect(self.connections_widget.update)
        self.input_widget.itemCollapsed.connect(self.connections_widget.update)

        self.input_widget.itemSelectionChanged.connect(
            self.__input_selection_changed
        )
        self.output_widget.itemSelectionChanged.connect(
            self.__output_selection_changed
        )

        self.layout().addWidget(self.output_widget, 0, 0)
        self.layout().addWidget(self.connections_widget, 0, 1)
        self.layout().addWidget(self.input_widget, 0, 2)

        self.layout().setColumnStretch(0, 2)
        self.layout().setColumnStretch(1, 1)
        self.layout().setColumnStretch(2, 2)

        self.connectButton = QPushButton(self)
        self.connectButton.clicked.connect(self.__disconnect_selected)
        self.connectButton.setEnabled(False)
        self.layout().addWidget(self.connectButton, 1, 1)

        self.dialogButtons = QDialogButtonBox(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok
        )
        self.dialogButtons.accepted.connect(self.accept)
        self.dialogButtons.rejected.connect(self.reject)
        self.layout().addWidget(self.dialogButtons, 2, 0, 1, 3)

        self.retranslateUi()

        self.__jack_client = jack_client
        self.__selected_in = None
        self.__selected_out = None

        self.connections = []
        self.update_graph()

    def retranslateUi(self):
        self.output_widget.setHeaderLabels(
            [translate("JackSinkSettings", "Output ports")]
        )
        self.input_widget.setHeaderLabels(
            [translate("JackSinkSettings", "Input ports")]
        )
        self.connectButton.setText(translate("JackSinkSettings", "Connect"))

    def set_connections(self, connections):
        self.connections = connections
        self.connections_widget.connections = self.connections
        self.connections_widget.update()

    def update_graph(self):
        input_ports = self.__jack_client.get_ports(is_audio=True, is_input=True)

        self.output_widget.clear()
        for port in range(8):
            self.output_widget.addTopLevelItem(
                QTreeWidgetItem(["output_" + str(port)])
            )

        self.input_widget.clear()
        clients = {}
        for port in input_ports:
            client_name = port.name[: port.name.index(":")]

            if client_name not in clients:
                clients[client_name] = ClientItem(client_name)
                self.input_widget.addTopLevelItem(clients[client_name])

            clients[client_name].add_port(port.name)

    def __input_selection_changed(self):
        if self.input_widget.selectedItems():
            self.__selected_in = self.input_widget.selectedItems()[0]
        else:
            self.__selected_in = None

        self.__check_selection()

    def __output_selection_changed(self):
        if self.output_widget.selectedItems():
            self.__selected_out = self.output_widget.selectedItems()[0]
        else:
            self.__selected_out = None

        self.__check_selection()

    def __check_selection(self):
        if self.__selected_in is not None and self.__selected_out is not None:
            output = self.output_widget.indexOfTopLevelItem(self.__selected_out)

            self.connectButton.clicked.disconnect()
            self.connectButton.setEnabled(True)

            if self.__selected_in.name in self.connections[output]:
                self.connectButton.setText(
                    translate("JackSinkSettings", "Disconnect")
                )
                self.connectButton.clicked.connect(self.__disconnect_selected)
            else:
                self.connectButton.setText(
                    translate("JackSinkSettings", "Connect")
                )
                self.connectButton.clicked.connect(self.__connect_selected)
        else:
            self.connectButton.setEnabled(False)

    def __connect_selected(self):
        output = self.output_widget.indexOfTopLevelItem(self.__selected_out)
        self.connections[output].append(self.__selected_in.name)
        self.connections_widget.update()
        self.__check_selection()

    def __disconnect_selected(self):
        output = self.output_widget.indexOfTopLevelItem(self.__selected_out)
        self.connections[output].remove(self.__selected_in.name)
        self.connections_widget.update()
        self.__check_selection()
