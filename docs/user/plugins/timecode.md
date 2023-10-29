# Timecode

This plugin can be used to send the <a href="https://en.wikipedia.org/wiki/Timecode" target="_blank">timecode</a> 
of your running audio files over _ArtNet_ or _MIDI_, to trigger cues inside a lighting control software 
or lighting desk such as "Chamsys MagicQ".<br>

This plugin works is meant as an alternative to the Chamsys Winamp plugin, which doesn't work under Linux.
To get a general idea what is this all about, have a look <a href="https://www.youtube.com/watch?v=Wu1iPkdzMJk">this video</a>.

```{note}

In order to use _ArtNet_, you need <a href="https://www.openlighting.org/ola/" target="_blank">OLA</a> installed, 
and a running OLA session on your computer.

To make sure that OLA is up and running, <a href="http://localhost:9090" tagret="_blank">http://localhost:9090</a>
should display the OLA interface.
```

## Preferences

You can configure the plugin in `File > Preferences > Plugins > Timecode Settings`

```{image} ../_static/timecode_settings.png
:alt: Timecode - Preferences
:align: center
```

* **Timecode Format:** choose between `SMPTE`, `FILM` and `EBU`.
  The format has to match the timecode used by the software which receives it.
* **Timecode Protocol:** the protocol used to send the timecode

## Cue Options (Timecode)

You can enable timecode for each media cues.

```{image} ../_static/timecode_cue_options.png
:alt: Timecode - Cue options
:align: center
```

* **Enable Timecode:** enables sending timecode for this cue
* **Replace HOURS by a static track number:** if checked, the `HOURS` field in
  the timecode is replaced by a static number, which can be used to identify
  which track currently sends timecode to your lighting software
* **Track number:** the value to use if the above option is checked

```{note}
If you work with multiple cue-lists on your lighting desk you than can choose
the following setup as example:

 * cuelist 1 refers to track 1 and uses HOUR=1
 * cuelist 2 refers to track 2 and uses HOUR=2
 * ... and so on
```
