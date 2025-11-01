from lisp.core.collections.nested_dict import NestedDict


def migrate(filename: str, session: NestedDict):
    for cue in session["cues"]:
        midi_triggers = NestedDict(cue).get("controller.midi", [])
        for trigger in midi_triggers:
            s = trigger[0].strip().split()
            trigger[0] = f"{s[0]} channel={s[1]} note={s[2]} velocity=0 time=0"