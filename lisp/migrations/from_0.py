import os.path
from urllib.parse import urlsplit

from lisp.core.collections.nested_dict import NestedDict


def migrate(filename: str, session: dict):
    session = NestedDict(session)

    session.move("application", "session")
    session.set(
        "session.layout_type",
        str(session.pop("session.layout")).replace(" ", ""),
    )

    for cue in session["cues"]:
        cue["_type_"] = cue.pop("type")

        if cue["_type_"] == "GstMediaCue":
            migrate_gst_media_cue(filename, cue)

    return session


def migrate_gst_media_cue(filename: str, cue: dict):
    cue = NestedDict(cue)

    cue.set(
        "media.pipe",
        (
            cue.get("media.pipe")
            .replace("URIInput!", "UriInput!")
            .replace("Fade!", "")
            .split("!")
        ),
    )

    cue.move("media.elements.URIInput", "media.elements.UriInput")
    cue.set(
        "media.elements.UriInput.uri",
        to_relative_uri(filename, cue.get("media.elements.UriInput.uri")),
    )

    cue.move("media.start_at", "media.start_time")

    cue.update(cue.pop("media.elements.Fade"))
    cue.move("fadein", "fadein_duration")
    cue.move("fadeout", "fadeout_duration")


def to_relative_uri(filename: str, uri: str):
    _uri = urlsplit(uri)

    if _uri.scheme == "file":
        return os.path.relpath(_uri.path, start=os.path.dirname(filename))

    return uri
