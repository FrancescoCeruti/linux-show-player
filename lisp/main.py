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
from itertools import chain

from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTranslator, QLocale, QLibraryInfo

from lisp import modules
from lisp import plugins
from lisp.application import Application
from lisp.ui import styles
from lisp.utils.configuration import config


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
    elif args.log == 'info':
        log = logging.INFO
    else:
        log = logging.WARNING

    logging.basicConfig(format='%(levelname)s:: %(message)s', level=log)

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
    QIcon.setThemeName(config['Theme']['icons'])
    styles.apply_style(config['Theme']['theme'])

    # Get the locale
    locale = args.locale
    if not locale:
        locale = QLocale().system().name()

    # Main app translations
    translator = QTranslator()
    translator.load('i18n/lisp_' + locale + '.qm')
    qt_app.installTranslator(translator)

    ui_translators = [translator]

    # Qt platform translation
    translator = QTranslator()
    translator.load("qt_" + locale,
                    QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    qt_app.installTranslator(translator)

    ui_translators.append(translator)

    # Modules and plugins translations
    for tr_file in chain(modules.translations(locale),
                         plugins.translations(locale)):
        translator = QTranslator()
        translator.load(tr_file)
        qt_app.installTranslator(translator)

        ui_translators.append(translator)

    # Create the application
    lisp_app = Application()
    # Load modules and plugins
    modules.load_modules()
    plugins.load_plugins()

    # Start/Initialize LiSP Application
    lisp_app.start(session_file=args.file)
    # Start Qt Application (block until exit)
    exit_code = qt_app.exec_()

    # Finalize the application
    lisp_app.finalize()
    # Exit
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
