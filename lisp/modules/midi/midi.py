from lisp.core.module import Module
from lisp.modules.midi.output_provider import MIDIOutputProvider
from lisp.utils.configuration import config

from lisp.modules.midi.input_handler import MIDIInputHandler
from lisp.modules.midi.midi_settings import MIDISettings
from lisp.ui.settings.app_settings import AppSettings


class Midi(Module):
    """
        Provide MIDI I/O functionality
    """

    def __init__(self):
        super().__init__()

        # Register the settings widget
        AppSettings.register_settings_widget(MIDISettings)

        port_name = config['MIDI']['InputDevice']
        backend_name = config['MIDI']['Backend']

        MIDIInputHandler(port_name=port_name, backend_name=backend_name)
        MIDIInputHandler().start()

        try:
            MIDIOutputProvider(port_name=port_name, backend_name=backend_name)
            MIDIOutputProvider().start()
        except Exception as e:
            MIDIInputHandler().stop()
            raise e

    def terminate(self):
        # Stop the MIDI-event Handler
        MIDIInputHandler().stop()
        MIDIOutputProvider().stop()
