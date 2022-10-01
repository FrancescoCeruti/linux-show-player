Cue Controls
============

Provide control over cues using keyboard and MIDI.

How to use
----------

Settings are provided per cue, and are accessible through a specific tab in the cue
settings window:

Keyboard
--------

.. image:: ../media/controller_settings_keyboard.png
    :alt: Linux Show Player - Controller settings - Keyboard
    :align: center

|

* **Key:** the key (character) that trigger the cue
* **Action:** the action to be executed when the key is pressed (Start/Stop/...)

New keys can be added/removed using the buttons at the table bottom. A key can
be any single character that the keyboard is able to insert, so special keys are
excluded, Upper/lower cases are considered, so "A" is not the same of "a".
In general, what is taken in account, it's not the pressed key, but the typed character.

MIDI
----

.. image:: ../media/controller_settings_midi.png
    :alt: Linux Show Player - Controller settings - MIDI
    :align: center

|

* **Type:** The message type (only *note_on/off*)
* **Channel:** MIDI message "channel"
* **Note:** MIDI message "note"
* **Action:** Action to execute when a matching message is received
* *The MIDI Note "velocity" is ignored*

New MIDI messages can be added/removed manually using the provided buttons,
or can be captured directly from the device, when doing so, a filter is provided
to select the type of messages to be captured.

The used MIDI device can be changed in the application settings ``File > Preferences > MIDI Settings``