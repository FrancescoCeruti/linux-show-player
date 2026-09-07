# This file is part of Linux Show Player
#
# Copyright 2026 Tobias Teichmann <tobias.teichmann@gmx.at>
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
import weakref
from collections import namedtuple
from types import MethodType
from typing import Callable, Optional

from lisp.core.util import weak_call_proxy
from lisp.plugins.gst_backend.video_output.window import VideoOutputWindow

logger = logging.getLogger(__name__)

_Attachment = namedtuple("_Attachment", "window_id on_orphaned")


class VideoOutputWindowManager:
    """Owns the set of persistent, named video-output windows.

    Windows are defined by app-level configuration and are independent of
    any cue/pipeline lifetime: they can be opened/closed manually (e.g. from
    a menu), and are opened automatically the first time a cue needs them.
    Several cues can target the same window at once (composited together by
    that window's own pipeline), while other cues target other windows in
    parallel.
    """

    CONFIG_KEY = "video_windows"

    def __init__(self, config: dict):
        self._config = config
        self._windows = {}
        self._channels = {}

    def definitions(self) -> list:
        return self._config.get(self.CONFIG_KEY, [])

    def _definition(self, window_id: str) -> Optional[dict]:
        for definition in self.definitions():
            if definition["id"] == window_id:
                return definition
        return None

    def list_windows(self) -> list:
        return [(d["id"], d["name"]) for d in self.definitions()]

    def get_window(self, window_id: str) -> Optional[VideoOutputWindow]:
        definition = self._definition(window_id)
        if definition is None:
            return None

        window = self._windows.get(window_id)
        if window is None:
            window = VideoOutputWindow(definition)
            self._windows[window_id] = window
        else:
            window.update_definition(definition)

        return window

    def is_open(self, window_id: str) -> bool:
        window = self._windows.get(window_id)
        return window is not None and window.is_open()

    def open(self, window_id: str):
        window = self.get_window(window_id)
        if window is not None:
            window.open()

    def close(self, window_id: str):
        window = self._windows.get(window_id)
        if window is not None:
            self._stop_orphaned_cues(window_id)
            window.close()

    def _resolve_window_id(
        self, window_id: str, window_name: str
    ) -> Optional[str]:
        if self._definition(window_id) is not None:
            return window_id

        if window_name:
            for definition in self.definitions():
                if definition.get("name") == window_name:
                    return definition["id"]

        return None

    def add_channel(
        self,
        window_id: str,
        window_name: str,
        channel: str,
        geometry: tuple = (0.0, 0.0, 1.0, 1.0),
        on_orphaned: Optional[Callable] = None,
    ):
        resolved_id = self._resolve_window_id(window_id, window_name)
        if resolved_id is None:
            fallback = self.definitions()
            if fallback:
                resolved_id = fallback[0]["id"]
                logger.warning(
                    f'Video output window "{window_name or window_id}" not '
                    f'found (channel "{channel}") - falling back to '
                    f'"{fallback[0]["name"]}"'
                )
            else:
                logger.warning(
                    f'Video output window "{window_name or window_id}" not '
                    f'found (channel "{channel}") - playing audio only'
                )
                return

        window = self.get_window(resolved_id)
        if not window.is_open():
            window.open()

        window.request_channel(channel, geometry)
        callback = None
        if on_orphaned is not None:
            if isinstance(on_orphaned, MethodType):
                callback = weak_call_proxy(weakref.WeakMethod(on_orphaned))
            else:
                callback = weak_call_proxy(weakref.ref(on_orphaned))
        self._channels[channel] = _Attachment(resolved_id, callback)

    def update_channel_geometry(self, channel: str, geometry: tuple):
        attachment = self._channels.get(channel)
        if attachment is None:
            return

        window = self._windows.get(attachment.window_id)
        if window is not None:
            window.update_channel_geometry(channel, geometry)

    def remove_channel(self, channel: str):
        attachment = self._channels.pop(channel, None)
        if attachment is None:
            return

        window = self._windows.get(attachment.window_id)
        if window is not None:
            window.release_channel(channel)

    def close_all(self):
        for window_id in list(self._windows):
            self._stop_orphaned_cues(window_id)
        for window in self._windows.values():
            window.close()

    def _stop_orphaned_cues(self, window_id: str):
        attachments = list(self._channels.items())
        for channel, attachment in attachments:
            if (
                attachment.window_id == window_id
                and attachment.on_orphaned is not None
            ):
                attachment.on_orphaned()
