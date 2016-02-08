#!/usr/bin/env python3

import lisp
from setuptools import find_packages, setup


setup(name='linux-show-player',
      version=lisp.__version__,
      author='Francesco Ceruti',
      author_email='ceppofrancy@gmail.com',
      url='http://linux-show-player.sourceforge.net/',
      description='Cue player for live shows',
      license='GPL+3',
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
