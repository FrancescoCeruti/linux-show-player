#!/usr/bin/env python3

import os
import re
from setuptools import find_packages, setup

import lisp


def find_files(directory, regex='.*', rel=''):
    """Search for files that match `regex` in `directory`."""
    paths = []
    for path, directories, file_names in os.walk(directory):
        for filename in file_names:
            file_path = os.path.join(path, filename)
            if re.match(regex, file_path):
                paths.append(file_path[len(rel):])
    return paths

# List the directories with icons to be installed
lisp_icons = find_files('lisp/ui/styles/icons', rel='lisp/ui/styles/')

# Setup function
setup(
    name='linux-show-player',
    author=lisp.__author__,
    author_email=lisp.__email__,
    version=lisp.__version__,
    license=lisp.__license__,
    url=lisp.__email__,
    description='Cue player for live shows',
    install_requires=[
        'sortedcontainers',
        'mido',
        'python-rtmidi',
        'JACK-Client',
        'scandir;python_version<"3.5"'
    ],
    packages=find_packages(),
    package_data={
        '': ['i18n/*.qm', '*.qss', '*.cfg'],
        'lisp.ui.styles': lisp_icons,
    },
    scripts=['linux-show-player']
)
