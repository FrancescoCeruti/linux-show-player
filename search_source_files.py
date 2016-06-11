#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
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

parser = argparse.ArgumentParser(description='Search for source files')
parser.add_argument('-r', '--root', help='Root directory', required=True)
parser.add_argument('--relative', help='Relative (to the root) sources paths',
                    default=False)
parser.add_argument('-e', '--exclude', nargs='*',
                    help='Paths to be ignored. A directory path with final "/" '
                         'will ignore only subdirectories, not files')
parser.add_argument('-x', '--exts', nargs='*', help='Source file extensions',
                    required=True)

args = parser.parse_args()

ROOT = args.root
RELATIVE = args.relative
EXCLUDE = args.exclude
EXTENSIONS = args.exts


def search_files(root, excluded=(), extensions=()):
    exc_regex = '^(' + '|'.join(excluded) + ').*' if excluded else '$^'
    ext_regex = '.*\.(' + '|'.join(extensions) + ')$' if extensions else '.*'

    for path, directories, filenames in os.walk(root):
        if re.match(exc_regex, path):
            continue

        if RELATIVE:
            path = path[len(ROOT):]
            if path.startswith(os.path.sep):
                path = path[len(os.path.sep):]

        for filename in filenames:
            if re.match(ext_regex, filename):
                if path:
                    filename = os.path.join(path, filename)
                yield filename


print(' '.join(search_files(ROOT, EXCLUDE, EXTENSIONS)))
