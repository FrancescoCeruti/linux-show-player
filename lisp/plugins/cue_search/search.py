# This file is part of Linux Show Player
#
# Copyright 2026 Francesco Ceruti <ceppofrancy@gmail.com>
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

from dataclasses import dataclass
from difflib import Match, SequenceMatcher
import re

from PyQt5.QtGui import QTextDocumentFragment

from lisp.cues.cue import Cue, CueState


@dataclass
class TextMatchResult:
    matches: list[Match]
    score: float


@dataclass
class CueMatchResult:
    cue: Cue
    score: int
    name: str
    description: str
    formatted_name: str
    formatted_description: str


def flatten_text(text: str):
    text = QTextDocumentFragment.fromHtml(text).toPlainText()
    return re.sub(r"\s+", " ", text).strip()


def match_text(text: str, query: str) -> TextMatchResult:
    matcher = SequenceMatcher(
        a=query.casefold(), b=text.casefold(), autojunk=False
    )

    matches = matcher.get_matching_blocks()
    matches = list(filter(lambda match: match.a == 0, matches))
    exactMatch = len(matches) > 0 and matches[0].size == len(query)

    return TextMatchResult(matches, matcher.ratio() + int(exactMatch))


def highlighted_matched_text(text: str, match_result: TextMatchResult):
    if not text:
        return ""

    if not match_result.matches:
        return text

    result = ""

    for n, current in enumerate(match_result.matches):
        if n == 0:
            result += text[: current.b]
        else:
            previous = match_result.matches[n - 1]
            result += text[previous.b + previous.size : current.b]

        result += "<b>" + text[current.b : current.b + current.size] + "</b>"

    return result + text[current.b + current.size :]


def search_cues(app, query: str) -> list[CueMatchResult]:
    matches = []

    for cue in app.layout.cues():
        name = flatten_text(cue.name)
        description = flatten_text(cue.description)

        name_match = match_text(name, query)
        description_match = match_text(description, query)

        if not name_match.matches and not description_match.matches:
            continue

        match = CueMatchResult(cue, 0, name, description, "", "")

        if name_match.matches:
            match.score += name_match.score
            match.formatted_name = highlighted_matched_text(name, name_match)

        if description_match.matches:
            match.score += description_match.score / 2
            match.formatted_description = highlighted_matched_text(
                description, description_match
            )

        matches.append(match)

    matches.sort(key=lambda item: (-item.score, item.cue.index))

    return matches


def running_cues(app) -> list[CueMatchResult]:
    matches = []

    for cue in app.layout.cues():
        if cue.state & CueState.IsRunning:
            name = flatten_text(cue.name)
            description = flatten_text(cue.description)

            matches.append(CueMatchResult(cue, 0, name, description, "", ""))

    return matches
