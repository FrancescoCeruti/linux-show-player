##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

import logging

from lisp.modules.action_cues.action_cues_factory import ActionCueFactory
from lisp.utils.dyamic_loader import load_classes
from lisp.utils.util import file_path


def initialize():
    for cue_name, cue_class in load_classes(file_path(__file__, 'cues')):
        ActionCueFactory.register_action_cue(cue_class)
        logging.debug('ACTION-CUES: Loaded "' + cue_name + '"')


def terminate():
    pass
