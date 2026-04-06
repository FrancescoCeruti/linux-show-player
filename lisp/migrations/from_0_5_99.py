from lisp.core.collections.dotdict import DotDict


def migrate(filename: str, session: DotDict):
    session.move("application", "session")
    session.set(
        "session.layout_type",
        str(session.pop("session.layout")).replace(" ", ""),
    )

    for cue in session["cues"]:
       match cue.get("next_action", ""):
        case "AutoNext":
            cue["next-action"] = "TriggerAfterWait"
        case "AutoFollow":
            cue["next-action"] = "TriggerAfterEnd"
