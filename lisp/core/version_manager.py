import copy
import json
from typing import Dict, Any


class VersionManager:
    def __init__(self, data: Dict[str, Any]):
        self.data = data
    
    def update_to_latest(self):
        if "meta" not in self.data:
            return self._convert_from_0_5()
        return self.data

    def _convert_from_0_5(self):
        self._transform_layout()
        self._transform_cues()
        return self.data

    def _transform_layout(self):
        layout = self.data.pop("application", {}).get("layout", "")
        self.data["session"] = {}
        self.data["session"]["layout_type"] = layout.replace(" ", "")

    def _transform_cues(self):
        for cue in self.data["cues"]:
            if cue["_type_"] == "MediaCue":
                cue["_type_"] = "GstMediaCue"
            if "_media_" in cue:
                cue["media"] = cue.pop("_media_")
            if "next_action" in cue:
                cue["next_action"] = (
                    cue.get("next_action", "")
                    .replace("AutoNext", "TriggerAfterWait")
                    .replace("AutoFollow", "TriggerAfterEnd")
                )
            self._transform_controller(cue)

    def _transform_controller(self, cue: dict):
        cue["controller"].setdefault("midi", [])
        cue["controller"].setdefault("osc", [])
        midi_entries = cue["controller"]["midi"]
        for entry in midi_entries:
            s = entry[0].strip().split()
            entry[0] = f"{s[0]} channel={s[1]} note={s[2]} velocity=0 time=0"
