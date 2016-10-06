#!/usr/bin/env python3

import os

from setuptools import find_packages, setup

import lisp


def package_files(directory, prefix=''):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        if path.startswith(prefix):
            path = path[len(prefix):]
        for filename in filenames:
            paths.append(os.path.join(path, filename))
    return paths


base_path = os.path.dirname(__file__)
lisp_icon_path = os.path.join(base_path, 'lisp/ui/styles/icons')
lisp_icons = package_files(lisp_icon_path, 'lisp/ui/styles/')


setup(name='linux-show-player',
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
      package_data={
          'lisp': ['default.cfg'],
          'lisp.ui': ['icon.png'],
          'lisp.ui.styles': lisp_icons,
          'lisp.ui.styles.dark': ['style.qss']
      },
      scripts=['linux-show-player'])
