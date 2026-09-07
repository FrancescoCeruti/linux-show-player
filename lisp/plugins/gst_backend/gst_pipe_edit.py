# This file is part of Linux Show Player
#
# Copyright 2016 Francesco Ceruti <ceppofrancy@gmail.com>
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
    QDialog,
    QGridLayout,
    QComboBox,
    QLabel,
    QListWidget,
    QAbstractItemView,
    QVBoxLayout,
    QPushButton,
    QDialogButtonBox,
    QWidget,
    QListWidgetItem,
)

from lisp.backend.media_element import ElementType, MediaType
from lisp.plugins.gst_backend import elements
from lisp.ui.icons import IconTheme
from lisp.ui.ui_utils import translate


class GstPipeEdit(QWidget):
    def __init__(self, pipe, app_mode=False, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QGridLayout())
        self.layout().setAlignment(Qt.AlignTop)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._app_mode = app_mode

        # Input selection
        self.inputLabel = QLabel(self)
        self.layout().addWidget(self.inputLabel, 0, 0, 1, 3)
        self.inputBox = QComboBox(self)
        self.layout().addWidget(self.inputBox, 1, 0, 1, 3)
        self.__init_inputs()

        # Current plugins list
        self.currentList = QListWidget(self)
        self.currentList.setDragEnabled(True)
        self.currentList.setDragDropMode(QAbstractItemView.InternalMove)
        self.layout().addWidget(self.currentList, 2, 0)

        # Available plugins list
        self.availableList = QListWidget(self)
        self.layout().addWidget(self.availableList, 2, 2)

        # Output selection
        self.audioOutputLabel = QLabel(self)
        self.layout().addWidget(self.audioOutputLabel, 3, 0, 1, 3)
        self.audioOutputBox = QComboBox(self)
        self.layout().addWidget(self.audioOutputBox, 4, 0, 1, 3)

        self.videoOutputLabel = QLabel(self)
        self.layout().addWidget(self.videoOutputLabel, 5, 0, 1, 3)
        self.videoOutputBox = QComboBox(self)
        self.layout().addWidget(self.videoOutputBox, 6, 0, 1, 3)

        self.__init_outputs()
        self.retranslateUi()

        # Add/Remove plugins buttons
        self.buttonsLayout = QVBoxLayout()
        self.layout().addLayout(self.buttonsLayout, 2, 1)
        self.layout().setAlignment(self.buttonsLayout, Qt.AlignHCenter)

        self.addButton = QPushButton(self)
        self.addButton.setIcon(IconTheme.get("go-previous-symbolic"))
        self.addButton.clicked.connect(self.__add_plugin)
        self.buttonsLayout.addWidget(self.addButton)
        self.buttonsLayout.setAlignment(self.addButton, Qt.AlignHCenter)

        self.delButton = QPushButton(self)
        self.delButton.setIcon(IconTheme.get("go-next-symbolic"))
        self.delButton.clicked.connect(self.__remove_plugin)
        self.buttonsLayout.addWidget(self.delButton)
        self.buttonsLayout.setAlignment(self.delButton, Qt.AlignHCenter)

        # Load the pipeline
        self.set_pipe(pipe)

    def retranslateUi(self):
        self.inputLabel.setText(translate("GstPipelineEdit", "Input"))
        self.audioOutputLabel.setText(translate("GstPipelineEdit", "Audio Output"))
        self.videoOutputLabel.setText(translate("GstPipelineEdit", "Video Output"))

    def set_pipe(self, pipe):
        if pipe:
            if not self._app_mode:
                self.inputBox.setCurrentText(
                    translate("MediaElementName", elements.input_name(pipe[0]))
                )

            for output in self._pipe_outputs(pipe):
                output_class = elements.all_elements()[output]
                if output_class.MediaType == MediaType.Video:
                    self.videoOutputBox.setCurrentText(
                        translate("MediaElementName", elements.output_name(output))
                    )
                else:
                    self.audioOutputBox.setCurrentText(
                        translate("MediaElementName", elements.output_name(output))
                    )

        self.__init_current_plugins(pipe)
        self.__init_available_plugins(pipe)

    def get_pipe(self):
        pipe = [] if self._app_mode else [self.inputBox.currentData()]
        for n in range(self.currentList.count()):
            pipe.append(self.currentList.item(n).data(Qt.UserRole))

        for output in (self.audioOutputBox.currentData(), self.videoOutputBox.currentData()):
            if output is not None:
                pipe.append(output)

        return tuple(pipe)

    @staticmethod
    def _pipe_outputs(pipe):
        """Return the trailing run of Output-type entries in `pipe` (0-2)."""
        all_elements = elements.all_elements()
        outputs = []
        for name in reversed(pipe):
            element_class = all_elements.get(name)
            if element_class is None or element_class.ElementType != ElementType.Output:
                break
            outputs.append(name)

        return outputs

    def __init_inputs(self):
        if self._app_mode:
            self.inputBox.setEnabled(False)
        else:
            inputs_by_name = {}
            for key, input in elements.inputs().items():
                inputs_by_name[translate("MediaElementName", input.Name)] = key

            for name in sorted(inputs_by_name):
                self.inputBox.addItem(name, inputs_by_name[name])

            self.inputBox.setEnabled(self.inputBox.count() > 1)

    def __init_outputs(self):
        self._populate_output_box(self.audioOutputBox, elements.audio_outputs())
        self._populate_output_box(self.videoOutputBox, elements.video_outputs())

    @staticmethod
    def _populate_output_box(box, outputs):
        box.addItem(translate("GstPipelineEdit", "None"), None)

        outputs_by_name = {}
        for key, output in outputs.items():
            outputs_by_name[translate("MediaElementName", output.Name)] = key

        for name in sorted(outputs_by_name):
            box.addItem(name, outputs_by_name[name])

        box.setEnabled(box.count() > 1)

    def __init_current_plugins(self, pipe):
        self.currentList.clear()

        # If not in app_mode, the first pipe element is the input
        # the last 0-2 are the output
        start = 0 if self._app_mode else 1
        end = len(pipe) - len(self._pipe_outputs(pipe))
        for plugin in pipe[start:end]:
            item = QListWidgetItem(
                translate("MediaElementName", elements.element_name(plugin))
            )
            item.setData(Qt.UserRole, plugin)
            self.currentList.addItem(item)

    def __init_available_plugins(self, pipe):
        self.availableList.clear()

        for plugin in elements.plugins():
            if plugin not in pipe:
                item = QListWidgetItem(
                    translate("MediaElementName", elements.plugin_name(plugin))
                )
                item.setData(Qt.UserRole, plugin)
                self.availableList.addItem(item)

    def __add_plugin(self):
        item = self.availableList.takeItem(self.availableList.currentRow())
        self.currentList.addItem(item)

    def __remove_plugin(self):
        item = self.currentList.takeItem(self.currentList.currentRow())
        self.availableList.addItem(item)


class GstPipeEditDialog(QDialog):
    def __init__(self, pipe, app_mode=False, **kwargs):
        super().__init__(**kwargs)
        self.setWindowTitle(translate("GstPipelineEdit", "Edit Pipeline"))
        self.setWindowModality(Qt.ApplicationModal)
        self.setMaximumSize(500, 400)
        self.setMinimumSize(500, 400)
        self.resize(500, 400)
        self.setLayout(QVBoxLayout())

        # GstPipeEdit
        self.pipeEdit = GstPipeEdit(pipe, app_mode=app_mode, parent=self)
        self.layout().addWidget(self.pipeEdit)

        # Confirm/Cancel buttons
        self.dialogButtons = QDialogButtonBox(self)
        self.dialogButtons.setStandardButtons(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok
        )
        self.layout().addWidget(self.dialogButtons)

        self.dialogButtons.accepted.connect(self.accept)
        self.dialogButtons.rejected.connect(self.reject)

    def get_pipe(self):
        return self.pipeEdit.get_pipe()
