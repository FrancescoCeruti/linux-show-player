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

from functools import lru_cache
from urllib.parse import urlsplit, urlunsplit, quote, unquote


class SessionURI:
    def __init__(self, uri: str = ""):
        split = urlsplit(uri)

        if split.scheme == "":
            self._uri = urlunsplit(
                ("file", "", quote(self.path_to_absolute(uri)), "", "")
            )
        else:
            self._uri = uri

    @property
    def relative_path(self):
        """The path relative to the session file. Make sense for local files."""
        path = unquote(urlsplit(self._uri).path)
        return self.path_to_relative(path)

    @property
    @lru_cache(maxsize=256)
    def absolute_path(self):
        """Unquoted "path" component of the URI."""
        # We can cache this, the absolute path doesn't change
        return unquote(urlsplit(self._uri).path)

    @property
    def uri(self):
        """The raw URI string."""
        return self._uri

    @property
    def unquoted_uri(self):
        """The URI string, unquoted."""
        return unquote(self._uri)

    @property
    def is_local(self):
        """True if the URI point to a local file."""
        return urlsplit(self._uri).scheme == "file"

    @classmethod
    def path_to_relative(cls, path):
        from lisp.application import Application

        return Application().session.rel_path(path)

    @classmethod
    def path_to_absolute(cls, path):
        from lisp.application import Application

        return Application().session.abs_path(path)
