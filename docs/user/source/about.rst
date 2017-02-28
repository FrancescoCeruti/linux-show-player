.. toctree::
   :hidden:
   :maxdepth: 1

About
=====

Linux Show Player (or LiSP for short) is a free cue player designed for
sound-playback in stage productions. The goal of the project is to provide a
complete playback software for musical plays, theater shows and similar.


Features
--------

Here a list of the main functionality offered by LiSP:

* Cart layout (buttons matrix) suited for touchscreens
* List layout suited for keyboards
* Large media-format support thanks to GStreamer
* Realtime sound effects: equalization, pitch shift, speed control, compression, ...
* Peak and ReplayGain normalization
* Undo/Redo changes
* Remote control over network, between two or more sessions
* ArtNet Timecode (via `OLA`_)
* MIDI support for cue triggering
* MIDI cues (send MIDI messages)
* Multi-language support (see `transifex`_ for a list of supported languages)


Project Status
--------------

Currently only GNU/Linux systems are supported.

The application is quite stable, is already been used for multiple performances
by different people, but, due to the heterogeneous nature of the GNU/Linux ecosystem,
my suggestion is to test it in a "working" environment to detect possible problems
with some configuration.


.. _transifex: https://www.transifex.com/linux-show-player/linux-show-player/
.. _OLA: https://www.openlighting.org/