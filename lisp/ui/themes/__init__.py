from lisp.ui.themes.dark.theme import DarkTheme
from lisp.ui.themes.theme import IconTheme

THEMES = {
    DarkTheme.Name: DarkTheme(),
}

ICON_THEMES = {
    'Symbolic': IconTheme('symbolic', 'lisp'),
    'Numix': IconTheme('numix', 'lisp')
}
