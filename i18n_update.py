#!/usr/bin/env python3
# This file is part of Linux Show Player
#
# Copyright 2019 Francesco Ceruti <ceppofrancy@gmail.com>
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

import os
import re
import subprocess
import sys
import shutil
from argparse import ArgumentParser
from pathlib import Path
from typing import Iterable

from scripts.pyts_update import TSTranslations, PyTrFinder, Obsolete

TS_DIR = Path("lisp/i18n/ts")
QM_DIR = Path("lisp/i18n/qm")
PYLUPDATE = "pylupdate5"
LRELEASE = "lrelease" if shutil.which("lrelease") else "lrelease-qt5"


def dirs_path(path: str):
    for entry in os.scandir(path):
        if entry.is_dir():
            yield Path(entry.path)


def existing_locales():
    for language_dir in dirs_path(TS_DIR):
        yield language_dir.name


def source_files(root: Path, extensions: Iterable[str], exclude: str = ""):
    for entry in root.glob("**/*"):
        if (
            entry.is_file()
            and entry.suffix in extensions
            and (not exclude or re.search(exclude, str(entry)) is None)
        ):
            yield entry


def modules_sources(
    modules_path: Iterable[Path],
    extensions: Iterable[str],
    exclude: str = "",
):
    for module_path in modules_path:
        if module_path.stem != "__pycache__":
            yield module_path.stem, source_files(
                module_path, extensions, exclude
            ),


def pylupdate(
    modules_path: Iterable[Path],
    locales: Iterable[str],
    options: Iterable[str] = (),
    extensions: Iterable[str] = (".py",),
    exclude: str = "",
):
    ts_files = modules_sources(modules_path, extensions, exclude)
    for locale in locales:
        locale_path = TS_DIR.joinpath(locale)
        locale_path.mkdir(exist_ok=True)
        for module_name, sources in ts_files:
            subprocess.run(
                (
                    PYLUPDATE,
                    *options,
                    *sources,
                    "-ts",
                    locale_path.joinpath(module_name + ".ts"),
                ),
                stdout=sys.stdout,
                stderr=sys.stderr,
            )


def pyts_update(
    modules_path: Iterable[Path],
    locales: Iterable[str],
    obsolete: Obsolete.Keep,
    extensions: Iterable[str] = (".py",),
    exclude: str = "",
):
    ts_files = modules_sources(modules_path, extensions, exclude)
    for locale in locales:
        locale_path = TS_DIR.joinpath(locale)
        locale_path.mkdir(exist_ok=True)
        for module_name, sources in ts_files:
            destination = locale_path.joinpath(module_name + ".ts")

            # Find the translations in python files
            finder = PyTrFinder(destination.as_posix(), language=locale)
            finder.find_in_files(sources)

            # Merge existing translations
            if destination.exists():
                existing_translations = TSTranslations.from_file(destination)
                finder.translations.update(
                    existing_translations, obsolete=obsolete
                )

            # Write the "ts" file
            finder.translations.write(destination)


def lrelease(locales: Iterable[str], options: Iterable[str] = ()):
    for locale in locales:
        qm_file = QM_DIR.joinpath("base_{}.qm".format(locale))
        locale_path = TS_DIR.joinpath(locale)
        ts_files = source_files(locale_path, extensions=(".ts",))

        subprocess.run(
            (LRELEASE, *options, *ts_files, "-qm", qm_file),
            stdout=sys.stdout,
            stderr=sys.stderr,
        )


if __name__ == "__main__":
    parser = ArgumentParser(description="i18n utility for LiSP")
    parser.add_argument(
        "locales",
        nargs="*",
        help="Locales to translate, ignore if --all is present",
    )
    parser.add_argument(
        "-a", "--all", help="Use existing locales", action="store_true"
    )
    parser.add_argument(
        "-n",
        "--noobsolete",
        help="If updating (--ts), discard obsolete strings",
        action="store_true",
    )
    parser.add_argument(
        "-q", "--qm", help="Release .qm files", action="store_true"
    )
    parser.add_argument(
        "-t", "--ts", help="Update .ts files", action="store_true"
    )
    parser.add_argument(
        "--pylupdate",
        help="Use pylupdate instead of the custom updater",
        action="store_true",
    )
    args = parser.parse_args()

    # Decide locales to use
    if args.all:
        locales = list(existing_locales())
        print(">>> USING LOCALES: ", ", ".join(locales))
    else:
        locales = args.locales or ("en",)

    # Update ts files
    if args.ts or not args.qm:
        print(">>> UPDATING ...")

        if args.pylupdate:
            # Use the pylupdate command
            options = []
            if args.noobsolete:
                options.append("-noobsolete")

            pylupdate(
                [Path("lisp")],
                locales,
                options=options,
                exclude="^lisp/plugins/|__pycache__",
            )
            pylupdate(
                dirs_path("lisp/plugins"),
                locales,
                options=options,
                exclude="__pycache__",
            )
        else:
            # Use our custom updater
            obsolete = Obsolete.Discard if args.noobsolete else Obsolete.Keep

            pyts_update(
                [Path("lisp")],
                locales,
                obsolete=obsolete,
                exclude="^lisp/plugins/|__pycache__",
            )
            pyts_update(
                dirs_path("lisp/plugins"),
                locales,
                obsolete=obsolete,
                exclude="__pycache__",
            )

    # Build the qm files
    if args.qm:
        print(">>> RELEASING ...")
        lrelease(locales)

    print(">>> DONE!")
