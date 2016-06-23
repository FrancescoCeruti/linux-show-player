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


lisp_icon_path = os.path.join(os.path.dirname(__file__), 'lisp/ui/icons')
lisp_ui_data = package_files(lisp_icon_path, 'lisp/ui/') + ['style/style.qss',
                                                            'icon.png']

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
          'lisp.ui': lisp_ui_data
      },
      scripts=['linux-show-player'])
