from lisp.utils.configuration import config

from lisp.modules.midi.midi import InputMidiHandler
from lisp.modules.midi.midi_settings import MIDISettings
from lisp.ui.settings.app_settings import AppSettings


def initialize():
    # Register the settings widget
    AppSettings.register_settings_widget(MIDISettings)

    # Initialize the MIDI-event Handler
    InputMidiHandler(port_name=config['MIDI']['InputDevice'],
                     backend_name=config['MIDI']['Backend'])
    # Start the MIDI-event Handler
    InputMidiHandler().start()


def terminate():
    # Stop the MIDI-event Handler
    InputMidiHandler().stop()
    # Unregister the settings widget
    AppSettings.unregister_settings_widget(MIDISettings)
