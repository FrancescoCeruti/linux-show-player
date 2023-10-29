# Integration cues

You can use this cues to interact with external devices or application MIDI and OSC protocols.

## MIDI Cue

This cue allows to send a MIDI message to the output device used by the application
(can be selected in the application preferences).

### Options (MIDI Settings)

```{image} ../_static/midi_cue_options.png
:alt: MIDI cue options
:align: center
```

* **MIDI Message:** Set what type of message to send
* **Attributes:** Depending on the message type different attributes can be edited

#### Supported MIDI messages

* Note ON
* Note OFF
* Polyphonic After-touch
* Control/Mode Change
* Program Change
* Channel After-touch
* Pitch Bend Change
* Song Select
* Song Position
* Start
* Stop
* Continue

## OSC cue

This cue allow to send OSC messages (the output port can be selected in the application preferences).

### Options (OSC Settings)

```{image} ../_static/osc_cue_options.png
:alt: OSC cue options
:align: center
```

* **Path:** the path to send the message to
* **Attributes:** The attributes of the message
  * **Type:** the attribute type
  * **Value:** the value of the attribute (starting value if fading)
  * **Fade To:** the value to reach if fading
  * **Fade:** fade the attributes
* **Fade:** fade settings
  * **Time:** fade duration in seconds
  * **Curve:** fade curve
