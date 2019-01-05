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

from os import cpu_count

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QRadioButton,
    QSpinBox,
    QCheckBox,
    QFrame,
    QLabel,
    QGridLayout,
    QButtonGroup,
    QProgressDialog,
)

from lisp.ui.ui_utils import translate


class GainUi(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowModality(Qt.ApplicationModal)
        self.setMaximumSize(380, 210)
        self.setMinimumSize(380, 210)
        self.resize(380, 210)

        self.setLayout(QGridLayout())

        # ReplayGain mode

        self.gainRadio = QRadioButton(self)
        self.gainRadio.setChecked(True)
        self.layout().addWidget(self.gainRadio, 0, 0)

        self.gainSpinBox = QSpinBox(self)
        self.gainSpinBox.setMaximum(150)
        self.gainSpinBox.setValue(89)
        self.layout().addWidget(self.gainSpinBox, 0, 1)

        # Normalize mode

        self.normalizeRadio = QRadioButton(self)
        self.layout().addWidget(self.normalizeRadio, 1, 0)

        self.normalizeSpinBox = QSpinBox(self)
        self.normalizeSpinBox.setRange(-100, 0)
        self.normalizeSpinBox.setEnabled(False)
        self.layout().addWidget(self.normalizeSpinBox, 1, 1)

        # All/Only selected

        self.selectionMode = QCheckBox(self)
        self.layout().addWidget(self.selectionMode, 2, 0, 1, 2)

        self.line = QFrame(self)
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.layout().addWidget(self.line, 3, 0, 1, 2)

        # Max threads (up to cpu count)

        self.cpuLabel = QLabel(self)
        self.layout().addWidget(self.cpuLabel, 4, 0)

        self.cpuSpinBox = QSpinBox(self)
        max_cpu = cpu_count()
        max_cpu = max_cpu if max_cpu is not None else 1
        self.cpuSpinBox.setRange(1, max_cpu)
        self.cpuSpinBox.setValue(max_cpu)
        self.layout().addWidget(self.cpuSpinBox, 4, 1)

        self.dialogButtons = QDialogButtonBox(self)
        self.dialogButtons.setStandardButtons(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.layout().addWidget(self.dialogButtons, 5, 0, 1, 2)

        self.normalizeRadio.toggled.connect(self.normalizeSpinBox.setEnabled)
        self.normalizeRadio.toggled.connect(self.gainSpinBox.setDisabled)

        self.dialogButtons.accepted.connect(self.accept)
        self.dialogButtons.rejected.connect(self.reject)

        self.modeGroup = QButtonGroup()
        self.modeGroup.addButton(self.gainRadio)
        self.modeGroup.addButton(self.normalizeRadio)

        self.retranslateUi()

    def retranslateUi(self):
        self.setWindowTitle(
            translate("ReplayGain", "ReplayGain / Normalization")
        )
        self.cpuLabel.setText(translate("ReplayGain", "Threads number"))
        self.selectionMode.setText(
            translate("ReplayGain", "Apply only to selected media")
        )
        self.gainRadio.setText(
            translate("ReplayGain", "ReplayGain to (dB SPL)")
        )
        self.normalizeRadio.setText(
            translate("ReplayGain", "Normalize to (dB)")
        )

    def mode(self):
        return 0 if self.gainRadio.isChecked() else 1

    def only_selected(self):
        return self.selectionMode.isChecked()

    def norm_level(self):
        return self.normalizeSpinBox.value()

    def ref_level(self):
        return self.gainSpinBox.value()

    def threads(self):
        return self.cpuSpinBox.value()


class GainProgressDialog(QProgressDialog):
    def __init__(self, maximum, parent=None):
        super().__init__(parent)

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle(translate("ReplayGain", "Processing files ..."))
        self.setMaximumSize(320, 110)
        self.setMinimumSize(320, 110)
        self.resize(320, 110)

        self.setMaximum(maximum)
        self.setLabelText("0 / {0}".format(maximum))

    def on_progress(self, value):
        if value == -1:
            # Hide the progress dialog
            self.setValue(self.maximum())
            self.deleteLater()
        else:
            self.setValue(self.value() + value)
            self.setLabelText("{0} / {1}".format(self.value(), self.maximum()))
