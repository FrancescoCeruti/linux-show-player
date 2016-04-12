#!/usr/bin/env python3

import lisp
from setuptools import find_packages, setup


setup(name='linux-show-player',
      author=lisp.__author__,
      author_email=lisp.__email__,
      version=lisp.__version__,
      license=lisp.__license__,
      url=lisp.__email__,
      description='Cue player for live shows',
      install_requires=['sortedcontainers', 'mido', 'python-rtmidi',
                        'JACK-Client',],
      packages=find_packages(),
      package_data={'lisp': ['default.cfg'],
                    'lisp.ui': ['icons/lisp/16/*',
                                'icons/lisp/22/*',
                                'icons/lisp/24/*',
                                'icons/lisp/scalable/*',
                                'icons/lisp/index.theme',
                                'icons/lisp/LICENSE.txt',
                                'style/style.qss',
                                'icon.png']},
      scripts=['linux-show-player'])
