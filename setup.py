#!/usr/bin/env python3

import lisp
from setuptools import find_packages, setup


setup(name='linuxshowplayer',
      version=lisp.__version__,
      author='Francesco Ceruti',
      author_email='ceppofrancy@gmail.com',
      url='https://code.google.com/p/linux-show-player/',
      description='Cue player for live shows',
      license='GPL+3',
      install_requires=['mido'],
      extras_require={'Jack MIDI': 'python-rtmidi'},
      packages=find_packages(),
      package_data={'lisp': ['default.cfg'],
                    'lisp.ui': ['icons/lisp/16/*',
                                'icons/lisp/22/*',
                                'icons/lisp/24/*',
                                'icons/lisp/scalable/*'
                                'icons/lisp/index.theme',
                                'icons/lisp/LICENSE.txt',
                                'style/style.qss',
                                'icon.png']},
      scripts=['linux-show-player'])
