try:
    import sys
    from lisp.utils import elogging
    from lisp.utils.configuration import config
    from .timecode import Timecode
except (ImportError, NameError) as e:
    elogging.warning('Plugin Timecode not loaded', details=str(e), dialog=False)
    config.set('Timecode', 'enabled', 'False')