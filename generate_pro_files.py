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
parser.add_argument('-e', '--exclude', nargs='*',
                    help='Paths to be ignored. A directory path with final "/" '
                         'will ignore only subdirectories, not files')
parser.add_argument('-x', '--exts', nargs='*', help='Source file EXTENSIONS',
                    required=True)
parser.add_argument('-l', '--locales', nargs='*', help='Locales of witch '
                                                       'generate translations')
parser.add_argument('--print', help='Just print the values', default=False)

args = parser.parse_args()

ROOT = args.root
EXCLUDE = args.exclude
EXTENSIONS = args.exts
LOCALES = args.locales
PRINT = args.print


def search_files():
    exc_regex = '^(' + '|'.join(EXCLUDE) + ').*' if EXCLUDE else '$^'
    ext_regex = '.*\.(' + '|'.join(EXTENSIONS) + ')$' if EXTENSIONS else '.*'

    for path, directories, filenames in os.walk(ROOT):
        if re.match(exc_regex, path):
            continue

        path = os.path.relpath(path, ROOT)

        for filename in filenames:
            if re.match(ext_regex, filename):
                if path:
                    filename = os.path.join(path, filename)
                yield filename


def create_pro_file():
    base_name = os.path.basename(os.path.normpath(ROOT))
    translations = 'TRANSLATIONS = '
    for local in LOCALES:
        translations += os.path.join('i18n', base_name + '_' + local + '.ts ')

    global RELATIVE
    RELATIVE = True
    files = 'SOURCES = ' + ' '.join(search_files())

    with open(os.path.join(ROOT, base_name + '.pro'), mode='w') as pro_file:
        pro_file.write(translations)
        pro_file.write(os.linesep)
        pro_file.write(files)


if not PRINT:
    create_pro_file()
else:
    print(' '.join(search_files()))
