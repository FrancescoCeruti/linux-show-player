#!/usr/bin/env python3

import os

from setuptools import find_packages, setup

import lisp


def data_dirs(directory, match='*', rel=''):
    paths = []
    for path, directories, file_names in os.walk(directory):
        paths.append(os.path.join(path[len(rel):], match))
    return paths


# List the directories with icons to be installed
lisp_icons = data_dirs('lisp/ui/styles/icons', rel='lisp/ui/styles/')

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
        'JACK-Client'
    ],
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['i18n/*.qm', '*.qss', '*.cfg'],
        'lisp.ui.styles': lisp_icons,
    },
    scripts=['linux-show-player']
)
