import os.path
from urllib.parse import urlsplit

from lisp.core.collections.dotdict import DotDict


def migrate(filename: str, session: DotDict):
    for cue in session["cues"]:
        if cue["_type_"] == "MediaCue":
            migrate_gst_media_cue(filename, DotDict(cue))


def migrate_gst_media_cue(filename: str, cue: DotDict):
    cue.set("_type_", "GstMediaCue")
    cue.move("_media_", "media")

    cue.set(
        "media.elements.UriInput.uri",
        to_relative_uri(filename, cue.get("media.elements.UriInput.uri")),
    )


def to_relative_uri(filename: str, uri: str):
    _uri = urlsplit(uri)

    if _uri.scheme == "file":
        return os.path.relpath(_uri.path, start=os.path.dirname(filename))

    return uri
