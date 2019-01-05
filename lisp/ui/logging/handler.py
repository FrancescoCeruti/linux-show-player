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

import logging

from lisp.core.signal import Signal, Connection


class QLoggingHandler(logging.Handler):
    """Base class to implement Qt-safe logging handlers.

    Instead of `emit` subclass must implement the `_emit` method.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # We need to append the new records while in the GUI thread, since
        # logging is asynchronous we need to use this "workaround"
        self.new_record = Signal()
        self.new_record.connect(self._emit, Connection.QtQueued)

    def emit(self, record):
        try:
            # The call will be processed in the Qt main-thread,
            # since the slot is queued, the call order is preserved
            self.new_record.emit(record)
        except Exception:
            self.handleError(record)

    def _emit(self, record):
        """Should implement the actual handling.

        This function is called in the Qt main-thread
        """
        pass


class LogModelHandler(QLoggingHandler):
    """Simple QLoggingHandler to log into a LogRecordModel"""

    def __init__(self, log_model, **kwargs):
        """
        :param log_model: the model to send the records to
        :type log_model: lisp.ui.logging.models.LogRecordModel
        """
        super().__init__(**kwargs)
        self._log_model = log_model

    def _emit(self, record):
        self._log_model.append(record)
