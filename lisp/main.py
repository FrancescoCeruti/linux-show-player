# This file is part of Linux Show Player
#
# Copyright 2018 Francesco Ceruti <ceppofrancy@gmail.com>
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
import os
import sys

import signal
from functools import partial
from logging.handlers import RotatingFileHandler

from PyQt5.QtCore import QLocale, QLibraryInfo, QTimer
from PyQt5.QtWidgets import QApplication

from lisp import (
    app_dirs,
    DEFAULT_APP_CONFIG,
    USER_APP_CONFIG,
    plugins,
    I18N_PATH,
)
from lisp.application import Application
from lisp.core.configuration import JSONFileConfiguration
from lisp.ui import themes
from lisp.ui.icons import IconTheme
from lisp.ui.ui_utils import install_translation, PyQtUnixSignalHandler


def main():
    # Parse the command-line arguments
    parser = argparse.ArgumentParser(description="Linux Show Player")
    parser.add_argument(
        "-f",
        "--file",
        default="",
        nargs="?",
        const="",
        help="Session file path",
    )
    parser.add_argument(
        "-l",
        "--log",
        choices=["debug", "info", "warning"],
        default="warning",
        help="Log level",
    )
    parser.add_argument("--locale", default="", help="Force specified locale")

    args = parser.parse_args()

    # Make sure the application user directories exist
    os.makedirs(app_dirs.user_config_dir, exist_ok=True)
    os.makedirs(app_dirs.user_data_dir, exist_ok=True)

    # Get logging level for the console
    if args.log == "debug":
        console_log_level = logging.DEBUG
        # If something bad happen at low-level (e.g. segfault) print the stack
        import faulthandler

        faulthandler.enable()
    elif args.log == "info":
        console_log_level = logging.INFO
    else:
        console_log_level = logging.WARNING

    # Setup the root logger
    default_formatter = logging.Formatter(
        "%(asctime)s.%(msecs)03d\t%(name)s\t%(levelname)s\t%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Create the console handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(default_formatter)
    stream_handler.setLevel(console_log_level)
    root_logger.addHandler(stream_handler)

    # Make sure the logs directory exists
    os.makedirs(app_dirs.user_log_dir, exist_ok=True)
    # Create the file handler
    file_handler = RotatingFileHandler(
        os.path.join(app_dirs.user_log_dir, "lisp.log"),
        maxBytes=10 * (2 ** 20),
        backupCount=5,
    )
    file_handler.setFormatter(default_formatter)
    root_logger.addHandler(file_handler)

    # Load application configuration
    app_conf = JSONFileConfiguration(USER_APP_CONFIG, DEFAULT_APP_CONFIG)

    # Create the QApplication
    qt_app = QApplication(sys.argv)
    qt_app.setApplicationName("Linux Show Player")
    qt_app.setQuitOnLastWindowClosed(True)

    # Get/Set the locale
    locale = args.locale
    if locale:
        QLocale().setDefault(QLocale(locale))

    logging.info(
        'Using "{}" locale -> {}'.format(
            QLocale().name(), QLocale().uiLanguages()
        )
    )

    # Qt platform translation
    qt_tr_path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    # install_translation("qt", tr_path=qt_tr_path)
    install_translation("qtbase", tr_path=qt_tr_path)
    # Main app translations
    install_translation("lisp", tr_path=I18N_PATH)

    # Set UI theme
    try:
        theme_name = app_conf["theme.theme"]
        themes.get_theme(theme_name).apply(qt_app)
        logging.info('Using "{}" theme'.format(theme_name))
    except Exception:
        logging.exception("Unable to load theme.")

    # Set LiSP icon theme (not the Qt one)
    try:
        icon_theme = app_conf["theme.icons"]
        IconTheme.set_theme_name(icon_theme)
        logging.info('Using "{}" icon theme'.format(icon_theme))
    except Exception:
        logging.exception("Unable to load icon theme.")

    # Initialize the application
    lisp_app = Application(app_conf)
    plugins.load_plugins(lisp_app)

    # Handle SIGTERM and SIGINT by quitting the QApplication
    def handle_quit_signal(*_):
        qt_app.quit()

    signal.signal(signal.SIGTERM, handle_quit_signal)
    signal.signal(signal.SIGINT, handle_quit_signal)

    with PyQtUnixSignalHandler():
        # Defer application start when QT main-loop starts
        QTimer.singleShot(0, partial(lisp_app.start, session_file=args.file))
        # Start QT main-loop, blocks until exit
        exit_code = qt_app.exec()

        # Finalize all and exit
        plugins.finalize_plugins()
        lisp_app.finalize()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
