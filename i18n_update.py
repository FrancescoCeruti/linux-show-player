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
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Iterable

TS_DIR = Path("lisp/i18n/ts")
QM_DIR = Path("lisp/i18n/qm")
PYLUPDATE = "pylupdate5"
LRELEASE = "lrelease"


def dirs_path(path: str):
    for entry in os.scandir(path):
        if entry.is_dir():
            yield Path(entry.path)


def existing_locales():
    for entry in os.scandir(TS_DIR):
        if entry.is_dir():
            yield entry.name


def source_files(root: Path, extensions: Iterable[str] = ("py",)):
    for ext in extensions:
        yield from root.glob("**/*.{}".format(ext))


def module_sources(module_path: Path, extensions: Iterable[str] = ("py",)):
    return module_path.stem, tuple(source_files(module_path, extensions))


def modules_sources(
    modules_path: Iterable[Path], extensions: Iterable[str] = ("py",)
):
    for module_path in modules_path:
        if not module_path.match("__*__"):
            yield module_sources(module_path, extensions)


def lupdate(
    modules_path: Iterable[Path],
    locales: Iterable[str],
    options: Iterable[str] = (),
    extensions: Iterable[str] = ("py",),
):
    ts_files = dict(modules_sources(modules_path, extensions))
    for locale in locales:
        locale_path = TS_DIR.joinpath(locale)
        locale_path.mkdir(exist_ok=True)
        for module_name, sources in ts_files.items():
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


def lrelease(locales: Iterable[str], options: Iterable[str] = ()):
    for locale in locales:
        qm_file = QM_DIR.joinpath("base_{}.qm".format(locale))
        locale_path = TS_DIR.joinpath(locale)
        ts_files = source_files(locale_path, extensions=("ts",))

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
        help="If --qm, discard obsolete strings",
        action="store_true",
    )
    parser.add_argument(
        "-q", "--qm", help="Release .qm files", action="store_true"
    )
    parser.add_argument(
        "-t", "--ts", help="Update .ts files", action="store_true"
    )
    args = parser.parse_args()

    # Decide what to do
    do_release = args.qm
    do_update = args.ts or not do_release

    # Decide locales to use
    if args.all:
        locales = list(existing_locales())
        print(">>> USING LOCALES: ", ", ".join(locales))
    else:
        locales = args.locales or ("en",)

    if do_update:
        print(">>> UPDATING ...")

        options = []
        if args.noobsolete:
            options.append("-noobsolete")

        lupdate(
            list(dirs_path("lisp/plugins")) + [Path("lisp")], locales, options
        )

    if do_release:
        print(">>> RELEASING ...")
        lrelease(locales)
