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
import os

from PyQt5.QtCore import QLocale, QLibraryInfo
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication

from lisp import plugins, USER_DIR
from lisp.application import Application
from lisp.core.configuration import AppConfig
from lisp.ui.styles import styles
from lisp.ui.ui_utils import install_translation


def main():
    # Parse the command-line arguments
    parser = argparse.ArgumentParser(description='Linux Show Player')
    parser.add_argument('-f', '--file', default='', nargs='?', const='',
                        help='Session file path')
    parser.add_argument('-l', '--log', choices=['debug', 'info', 'warning'],
                        default='warning', help='Log level')
    parser.add_argument('--locale', default='', help='Force specified locale')

    args = parser.parse_args()

    # Set the logging level
    if args.log == 'debug':
        log = logging.DEBUG

        # If something bad happen at low-level (e.g. segfault) print the stack
        import faulthandler
        faulthandler.enable()
    elif args.log == 'info':
        log = logging.INFO
    else:
        log = logging.WARNING

    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(levelname)s:: %(message)s',
        datefmt='%H:%M:%S',
        level=log
    )

    # Create (if not present) user directory
    os.makedirs(os.path.dirname(USER_DIR), exist_ok=True)

    # Create the QApplication
    qt_app = QApplication(sys.argv)
    qt_app.setApplicationName('Linux Show Player')
    qt_app.setQuitOnLastWindowClosed(True)

    # Force light font, for environment with "bad" QT support.
    appFont = qt_app.font()
    appFont.setWeight(QFont.Light)
    qt_app.setFont(appFont)
    # Set icons and theme from the application configuration
    QIcon.setThemeSearchPaths(styles.IconsThemePaths)
    QIcon.setThemeName(AppConfig()['Theme']['Icons'])
    styles.apply_style(AppConfig()['Theme']['Theme'])

    # Get/Set the locale
    locale = args.locale
    if locale:
        QLocale().setDefault(QLocale(locale))

    logging.info('Using {} locale'.format(QLocale().name()))

    # Qt platform translation
    install_translation('qt', tr_path=QLibraryInfo.location(
        QLibraryInfo.TranslationsPath))
    # Main app translations
    install_translation('lisp', tr_path=os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'i18n'))

    # Create the application
    lisp_app = Application()
    # Load plugins
    plugins.load_plugins(lisp_app)

    # Start/Initialize LiSP Application
    lisp_app.start(session_file=args.file)
    # Start Qt Application (block until exit)
    exit_code = qt_app.exec_()

    # Finalize plugins
    plugins.finalize_plugins()
    # Finalize the application
    lisp_app.finalize()
    # Exit
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
