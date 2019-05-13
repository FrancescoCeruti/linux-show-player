# This file is part of Linux Show Player
#
# Copyright 2017 Francesco Ceruti <ceppofrancy@gmail.com>
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

import os

from lisp.core.has_properties import Property, HasInstanceProperties
from lisp.core.signal import Signal
from lisp.core.util import typename


class Session(HasInstanceProperties):
    layout_type = Property(default="")
    layout = Property(default={})

    session_file = Property(default="")

    def __init__(self, layout):
        super().__init__()
        self.finalized = Signal()

        self.layout_type = typename(layout)
        self.layout = layout

        self.cue_model = layout.cue_model

    def name(self):
        """Return the name of session, depending on the session-file."""
        if self.session_file:
            return os.path.splitext(os.path.basename(self.session_file))[0]
        else:
            return "Untitled"

    def dir(self):
        """Return the current session-file path."""
        if self.session_file:
            return os.path.dirname(self.session_file)
        else:
            return os.path.expanduser("~")

    def abs_path(self, rel_path):
        """Return an absolute version of the given path."""
        if not os.path.isabs(rel_path):
            return os.path.normpath(os.path.join(self.dir(), rel_path))

        return rel_path

    def rel_path(self, abs_path):
        """Return a relative (to the session-file) version of the given path."""
        return os.path.relpath(abs_path, start=self.dir())

    def finalize(self):
        self.layout.finalize()
        self.cue_model.reset()

        self.finalized.emit()
