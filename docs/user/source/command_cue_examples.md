Command Cues Examples
=====================

Examples of ``Command cues`` to control other programs using LiSP:


LibreOffice
-----------

Impress
^^^^^^^

* **Start slideshow:** ``xdotool key --window "$(xdotool search --class Libreoffice | head -n1)" F5`` (requires xdotool)
* **Next slide:** ``xdotool key --window "$(xdotool search --class Libreoffice | head -n1)" Right`` (requires xdotool)

VLC
---

* **Playback a file (full-screen):** ``vlc -f <file/path>``

MPV PLAYER
----------

Allows to use a single mpv player instance, which is controlled through their json IPC interface.
Use "Start Player" to init the player, you have to edit --geometry according
to your display setup, "Load File" to play a Video file (you have to fill in the
$MEDIA variable at the beginning of this command). The videos are played and
stays open until next file is started. Images work too, so it is possible add add
black images between the videos if needed.

* **Start Player:** ``mpv --input-ipc-server=/tmp/mpvsocket --idle --keep-open=always --osc=no --fullscreen --geometry=1920:0``
* **Load File:** ``MEDIA="<file/path>"; printf '{ "command": ["loadfile", "%s"] }\n' $MEDIA|socat - /tmp/mpvsocket``
* *A complete set of commands can be downloaded and imported as preset in the GitHub releases page.*
