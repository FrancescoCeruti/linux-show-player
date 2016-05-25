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

parser = argparse.ArgumentParser(description='Generate .pro qt files')
parser.add_argument('-r', '--root', help='Root of the project', required=True)
parser.add_argument('-e', '--exclude', nargs='*',
                    help='Paths to be ignored. A directory path with final "/" '
                         'will ignore only subdirectories, not files')
parser.add_argument('-x', '--exts', nargs='*', help='Source file extensions',
                    required=True)
parser.add_argument('-o', '--out', help='Destination file name', required=True)
parser.add_argument('-s', '--subdirs', nargs='*', help='Subdirs')
parser.add_argument('-t', '--tspath', help='Translations path')
parser.add_argument('-l', '--locales', nargs='+', help='Translations files')

args = parser.parse_args()

ROOT = args.root
EXCLUDE = args.exclude
EXTENSIONS = args.exts
DESTINATION = args.out
if args.subdirs is not None:
    SUBDIRS = ' '.join(args.subdirs)
else:
    SUBDIRS = ''

TS_PATH = args.tspath
LOCALES = args.locales
if TS_PATH is not None and LOCALES is not None:
    TRANSLATIONS = ' '.join(os.path.join(TS_PATH, locale) for locale in LOCALES)
else:
    TRANSLATIONS = ''

TEMPLATE = '''\
CODECFORSRC     = UTF-8
TEMPLATE        = subdirs
SOURCES         = {}
SUBDIRS         = {}
TRANSLATIONS    = {}
'''


def search_files(root, excluded=(), extensions=()):
    exc_regex = '^(' + '|'.join(excluded) + ').*' if excluded else '$^'
    ext_regex = '.*\.(' + '|'.join(extensions) + ')$' if extensions else '.*'

    for path, directories, filenames in os.walk(root):
        if re.match(exc_regex, path):
            continue

        for filename in filenames:
            if re.match(ext_regex, filename):
                yield os.path.join(path, filename)


SOURCES = ' '.join(search_files(ROOT, EXCLUDE, EXTENSIONS))

with open(DESTINATION, mode='w', encoding='utf-8') as f:
    f.write(TEMPLATE.format(SOURCES, SUBDIRS, TRANSLATIONS))
