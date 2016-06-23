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
import logging
import sys

from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication

from lisp import modules
from lisp import plugins
from lisp.application import Application
from lisp.ui import styles
from lisp.utils.configuration import config


def _exec(qt_app, LiSP_app):
    # Start PyQt main loop
    qt_app.exec_()

    # Finalize the application
    LiSP_app.finalize()


def main():
    # Create and parse the command-line arguments
    parser = argparse.ArgumentParser(description='Linux Show Player')
    parser.add_argument('-f', '--file', default='', nargs='?', const='',
                        help='Session file path')
    parser.add_argument('-l', '--log', choices=['debug', 'info', 'warning'],
                        default='warning', help='Log level')

    args = parser.parse_args()

    # Set the logging level
    if args.log == 'debug':
        log = logging.DEBUG
    elif args.log == 'info':
        log = logging.INFO
    else:
        log = logging.WARNING

    logging.basicConfig(format='%(levelname)s:: %(message)s', level=log)

    # Create the QApplication
    app = QApplication(sys.argv)
    app.setApplicationName('Linux Show Player')
    app.setQuitOnLastWindowClosed(True)

    # Force light font, for environment with "bad" QT support.
    appFont = app.font()
    appFont.setWeight(QFont.Light)
    app.setFont(appFont)
    # Set icons and theme from the application configuration
    QIcon.setThemeSearchPaths(styles.IconsThemePaths)
    QIcon.setThemeName(config['Theme']['icons'])
    styles.apply_style(config['Theme']['theme'])

    # Create the application
    LiSP_app = Application()
    # Load modules and plugins
    modules.load_modules()
    plugins.load_plugins()
    # Start the application
    LiSP_app.start(session_file=args.file)

    # Start the application
    sys.exit(_exec(app, LiSP_app))


if __name__ == "__main__":
    main()
