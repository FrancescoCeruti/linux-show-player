##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from os import path

from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QStyleFactory, qApp

from lisp.ui.style import style  # @UnusedImport


absPath = path.abspath(path.join(path.dirname(__file__))) + '/'

QLiSPIconsThemePaths = [absPath + 'icons']
QLiSPIconsThemeName = 'lisp'

QLiSPTheme = ''
with open(absPath + 'style/style.qss', mode='r', encoding='utf-8') as f:
    QLiSPTheme = f.read()


def get_styles():
    return QStyleFactory.keys() + ['LiSP']


def apply_style(style_name):
    if style_name == 'LiSP':
        qApp.setStyleSheet(QLiSPTheme)

        # Change link color
        palette = qApp.palette()
        palette.setColor(QPalette.Link, QColor(65, 155, 230))
        palette.setColor(QPalette.LinkVisited, QColor(43, 103, 153))
        qApp.setPalette(palette)
    else:
        qApp.setStyleSheet('')
        qApp.setStyle(QStyleFactory.create(style_name))
