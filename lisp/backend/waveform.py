# This file is part of Linux Show Player
#
# Copyright 2020 Francesco Ceruti <ceppofrancy@gmail.com>
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
import pickle
from abc import ABCMeta, abstractmethod
from os import path, makedirs

from lisp import DEFAULT_CACHE_DIR
from lisp.application import Application
from lisp.core.signal import Signal
from lisp.core.util import file_hash

logger = logging.getLogger(__name__)


class Waveform(metaclass=ABCMeta):
    CACHE_VERSION = "1"
    CACHE_DIR_NAME = "waveforms"
    MAX_DECIMALS = 5

    def __init__(self, uri, duration, max_samples=1280, cache=True):
        self.ready = Signal()
        self.rms_samples = []
        self.peak_samples = []
        self.max_samples = max_samples
        self.duration = duration
        self.uri = uri
        self.failed = Signal()
        self._hash = None
        self.cache = cache

    def cache_dir(self):
        cache_dir = Application().conf.get("cache.position", "")
        if not cache_dir:
            cache_dir = DEFAULT_CACHE_DIR

        return path.join(cache_dir, self.CACHE_DIR_NAME)

    def cache_path(self, refresh=True):
        """Return the path of the file used to cache the waveform.

        The path name is based on the hash of the source file, which will be
        calculated and saved the first time.
        """
        scheme, _, file_path = self.uri.partition("://")
        if scheme != "file":
            return ""

        if not self._hash or refresh:
            self._hash = file_hash(
                file_path, digest_size=16, person=self.CACHE_VERSION.encode(),
            )

        return path.join(
            path.dirname(file_path), self.cache_dir(), self._hash + ".waveform",
        )

    def load_waveform(self):
        """ Load the waveform.

        If the waveform is ready returns True, False otherwise, in that case
        the "ready" signal will be emitted when the processing is complete.
        """
        if self.is_ready() or self._from_cache():
            # The waveform has already been loaded, or is in cache
            return True
        else:
            # Delegate the actual work to concrete subclasses
            return self._load_waveform()

    def is_ready(self):
        return bool(self.peak_samples and self.rms_samples)

    def clear(self):
        self.rms_samples = []
        self.peak_samples = []

    @abstractmethod
    def _load_waveform(self):
        """ Implemented by subclasses. Load the waveform from the file.

        Should return True if the waveform is already available, False
        if otherwise.
        Once available the "ready" signal should be emitted.
        """

    def _from_cache(self):
        """ Retrieve data from a cache file, if caching is enabled. """
        try:
            cache_path = self.cache_path()
            if self.cache and path.exists(cache_path):
                with open(cache_path, "rb") as cache_file:
                    cache_data = pickle.load(cache_file)
                    if len(cache_data) >= 2:
                        self.peak_samples = cache_data[0]
                        self.rms_samples = cache_data[1]

                        logger.debug(
                            f"Loaded waveform from the cache: {cache_path}"
                        )
                        return True
        except Exception:
            pass

        return False

    def _to_cache(self):
        """ Dump the waveform data to a file, if caching is enabled. """
        if self.cache:
            cache_path = self.cache_path()
            cache_dir = path.dirname(cache_path)
            if cache_dir:
                if not path.exists(cache_dir):
                    makedirs(cache_dir, exist_ok=True)

                with open(cache_path, "wb") as cache_file:
                    pickle.dump(
                        (self.peak_samples, self.rms_samples,), cache_file,
                    )

                logger.debug(f"Dumped waveform to the cache: {cache_path}")
