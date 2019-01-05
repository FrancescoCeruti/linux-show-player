#!/usr/bin/env python3
#
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

import argparse
import os
import re
import subprocess
import sys

try:
    from os import scandir, getcwd
except ImportError:
    from scandir import scandir


parser = argparse.ArgumentParser(description="i18n utility for LiSP")
parser.add_argument(
    "locales", nargs="*", help="Locales of witch generate translations"
)
parser.add_argument(
    "-n", "--noobsolete", help="Discard obsolete strings", action="store_true"
)
parser.add_argument("-q", "--qm", help="Release .qm files", action="store_true")


args = parser.parse_args()

# pylupdate command with arguments
PYLUPDATE_CMD = ["pylupdate5"]
if args.noobsolete:
    PYLUPDATE_CMD.append("-noobsolete")


def existing_locales():
    for entry in scandir("lisp/i18n/ts/"):
        if entry.is_dir():
            yield entry.name


# Locales of which generate translations files
LOCALES = args.locales
if not LOCALES:
    LOCALES = ["en"]
elif LOCALES == "*":
    LOCALES = list(existing_locales())
    print(">>> UPDATE EXISTING:", ", ".join(LOCALES))


def search_files(root, exclude=(), extensions=()):
    exc_regex = "^(" + "|".join(exclude) + ").*" if exclude else "$^"
    ext_regex = ".*\.(" + "|".join(extensions) + ")$" if extensions else ".*"

    for path, directories, filenames in os.walk(root):
        if re.match(exc_regex, path):
            continue

        path = os.path.relpath(path, root)

        for filename in filenames:
            if re.match(ext_regex, filename):
                if path:
                    filename = os.path.join(path, filename)
                yield filename


def create_pro_file(root, exclude=(), extensions=("py",)):
    base_name = os.path.basename(os.path.normpath(root))
    back = "../" * (len(root.split("/")) - 1)

    translations = "TRANSLATIONS = "
    for locale in LOCALES:
        translations += os.path.join(
            back, "i18n/ts/", locale, base_name + ".ts "
        )

    files = "SOURCES = " + " ".join(search_files(root, exclude, extensions))

    with open(os.path.join(root, base_name + ".pro"), mode="w") as pro_file:
        pro_file.write(translations)
        pro_file.write(os.linesep)
        pro_file.write(files)


def generate_for_submodules(path, qm=False):
    modules = [entry.path for entry in scandir(path) if entry.is_dir()]
    for module in modules:
        if "__pycache__" not in module:
            create_pro_file(module)
            p_file = os.path.join(module, os.path.basename(module) + ".pro")
            if qm:
                subprocess.run(
                    ["lrelease", p_file], stdout=sys.stdout, stderr=sys.stderr
                )
            else:
                subprocess.run(
                    PYLUPDATE_CMD + [p_file],
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                )


print(">>> UPDATE TRANSLATIONS FOR APPLICATION")
create_pro_file("lisp", exclude=("lisp/plugins/",))
if args.qm:
    subprocess.run(
        ["lrelease", "lisp/lisp.pro"], stdout=sys.stdout, stderr=sys.stderr
    )
else:
    subprocess.run(
        PYLUPDATE_CMD + ["lisp/lisp.pro"], stdout=sys.stdout, stderr=sys.stderr
    )

print(">>> UPDATE TRANSLATIONS FOR PLUGINS")
generate_for_submodules("lisp/plugins", qm=args.qm)
