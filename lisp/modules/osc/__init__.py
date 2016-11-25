try:
    from lisp.utils import elogging
    from .osc import Osc
except ImportError as error:
    elogging.error(e, 'pyliblo not found', dialog=False)