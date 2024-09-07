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

    return session
