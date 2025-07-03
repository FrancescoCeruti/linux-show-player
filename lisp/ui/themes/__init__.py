from os import path

from lisp.core.loading import load_classes
from PyQt5.QtWidgets import QStyleFactory
from .system import System

_THEMES = {}
_THEME_NAMES = {}
_THEME_DEFAULT = ''

def load_themes():
    if not _THEMES:
        _THEMES[''] = System('')
        _THEME_NAMES[''] = 'System'
        for name, theme in load_classes(__package__, path.dirname(__file__)):
            if name != 'System':
                _THEMES[name] = theme()
                _THEME_NAMES[name] = name + ' (Lisp)'
        for name in QStyleFactory.keys():
            _THEMES['system.' + name] = System(name)
            _THEME_NAMES['system.' + name] = name + ' (Qt)'

def themes_names():
    load_themes()
    return _THEME_NAMES

def get_theme_text(theme_name):
    load_themes()
    return _THEME_NAMES.get(theme_name, _THEME_NAMES[_THEME_DEFAULT])

def get_theme(theme_name):
    load_themes()
    return _THEMES.get(theme_name, _THEMES[_THEME_DEFAULT])
