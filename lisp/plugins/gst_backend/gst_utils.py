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
# along with Linux Show Player.  If not, see <http://www.gnu.org/licenses/>

from lisp.backend.audio_utils import audio_file_duration
from lisp.core.session_uri import SessionURI
from lisp.plugins.gst_backend.gi_repository import Gst, GstPbutils


def gst_uri_duration(uri: SessionURI):
    # First try to use the base implementation, because it's faster
    duration = 0
    if uri.is_local:
        duration = audio_file_duration(uri.absolute_path)

    try:
        # Fallback to GStreamer discoverer
        # TODO: we can probabbly make this faster see https://github.com/mopidy/mopidy/blob/develop/mopidy/audio/scan.py
        if duration <= 0:
            duration = gst_uri_metadata(uri).get_duration() // Gst.MSECOND
    finally:
        return duration if duration >= 0 else 0


def gst_mime_types():
    for gtf in Gst.TypeFindFactory.get_list():
        caps = gtf.get_caps()

        if caps is not None:
            for i in range(caps.get_size()):
                mime = caps.get_structure(i).to_string()
                extensions = gtf.get_extensions()
                yield mime, extensions


def gst_uri_metadata(uri: SessionURI):
    """Discover media-file metadata using GStreamer."""
    try:
        discoverer = GstPbutils.Discoverer()
        return discoverer.discover_uri(uri.uri)
    except Exception:
        pass


def gst_parse_tags_list(gst_tag_list):
    """Takes a GstTagList object and returns a dict.

    Adapted from https://github.com/ch3pjw/pyamp
    """
    parsed_tags = {}

    def parse_tag(gst_tag_list, tag_name, parsed_tags):
        parsed_tags[tag_name] = gst_tag_list.get_value_index(tag_name, 0)

    gst_tag_list.foreach(parse_tag, parsed_tags)
    return parsed_tags


class GstError(Exception):
    """Used to wrap GStreamer debug messages for the logging system."""
