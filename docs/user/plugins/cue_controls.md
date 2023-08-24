# Cue Controls

Provide control over cues using keyboard, MIDI or OSC.

## Keyboard

Trigger the cue with a custom key

```{image} ../_static/cue_control_options_keyboard.png
:alt: Cue Control - Keyboard
:align: center
```

* **Shortcut:** the shortcut that trigger the cue
* **Action:** the action to execute (Default/Start/Stop/...)

New keys can be added and removed using the buttons at the bottom of the list.

## MIDI

Trigger the cue when a MIDI message is received

```{image} ../_static/cue_control_options_midi.png
:alt: Cue Control - MIDI
:align: center
```

* **Type:** The message type
* **Data 1/2/3:** MIDI message data
* **Action:** the action to execute (Default/Start/Stop/...)

New messages can be added and removed using the provided buttons,
to edit `Duble-Click` on the value you want to change.

Messages can be captured directly from the device using the **Capture** button,
a filter is provided to select the type of messages to be captured.

```{note}
The used MIDI device can be changed in the application settings `File > Preferences > Plugins > MIDI settings`
```

## OSC

Trigger the cue when an OSC message is received

```{image} ../_static/cue_control_options_osc.png
:alt: Cue Control - OSC
:align: center
```

* **Path:** OSC path
* **Types/Attributes:** The message expected attributes types, and values
* **Action:** the action to execute (Default/Start/Stop/...)

New messages can be added and removed using the provided buttons,
to edit `Duble-Click` on the value you want to change.

Messages can be captured directly using the **Capture** button.