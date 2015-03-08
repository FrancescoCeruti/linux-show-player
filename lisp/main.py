##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

import argparse
import logging
import sys

from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication
from lisp.ui import styles
from lisp.utils.configuration import config

from lisp.application import Application


def _exec(qt_app, LiSP_app):
    # Start PyQt main loop
    qt_app.exec_()

    # Finalize the application
    LiSP_app.finalize()


def main():
    # Create and parse the command-line arguments
    parser = argparse.ArgumentParser(description='Linux Show Player')
    parser.add_argument('-f', '--file', default='', help="Session file path")
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

    # Force light font, for environment with bad QT support.
    appFont = app.font()
    appFont.setWeight(QFont.Light)
    app.setFont(appFont)
    # Add icons set
    QIcon.setThemeSearchPaths(styles.IconsThemePaths)
    QIcon.setThemeName(styles.IconsThemeName)
    # Load the theme
    styles.apply_style(config['Theme']['current'])

    # Create the application
    LiSP_app = Application()  # @UnusedVariable
    LiSP_app.start(filepath=args.file)

    # Start the application
    sys.exit(_exec(app, LiSP_app))


if __name__ == "__main__":
    main()
