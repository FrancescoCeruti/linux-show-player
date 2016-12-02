from lisp.core.configuration import config

try:
    import ola
except ImportError:
    ola = False
    raise ImportError('OLA module not found, plugin not loaded.')

if ola:
    from .timecode import Timecode
