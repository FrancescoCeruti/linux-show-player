# Misc cues

Cues that don’t fit others categories

## Command Cue

This cue allow to execute a shell command, until the command runs the cue is
`running` and can be stopped, doing so will terminate the command.

To see the command output, LiSP should be launched from a terminal, and
`Discard command output` must be disabled.

```{danger}
The cue will execute **any** command you supply!<br>
Be sure to understand what you're doing, and avoid dangerous and untrested commands.
```

### Options (Command Cue)

```{image} ../_static/command_cue_options.png
:alt: Command Cue options
:align: center
```

* **Command:** the command line to be executed (as in a shell)
* **Discard command output:** when enabled the command output is discarded
* **Ignore command errors:** when enabled errors are not reported
* **Kill instead of terminate:** when enabled, on stop, the command is killed (abruptly interrupted by the OS)
* **Run the command on the host system (_Available only for flatpak installations._):**
    When disabled the command will be run inside the sandbox, this will prevent access to any application
    installed on your "host" system

### Examples

Here you can find some examples of commands to control other applications

#### LibreOffice Impress

* **Start slideshow:** `xdotool key --window "$(xdotool search --class Libreoffice | head -n1)" F5`
* **Next slide:** `xdotool key --window "$(xdotool search --class Libreoffice | head -n1)" Right`

```{note}
Requires xdotool
```

#### VLC

* **Playback a file (full-screen):** `vlc -f <file/path>`

#### MPV PLAYER

Allows to use a single mpv player instance, controlled through their json IPC interface.

**Start Player** to init the player, you have to edit `--geometry` according
to your display setup.<br>
**Load File** to play a Video file (you have to fill in the `$MEDIA` variable at the beginning of this command).

The videos are played and stays open until next file is started.
Images work too, so it is possible add black images between the videos if needed.

* **Start Player:** `mpv --input-ipc-server=/tmp/mpvsocket --idle --keep-open=always --osc=no --fullscreen --geometry=1920:0`
* **Load File:** `MEDIA="<file/path>"; printf '{ "command": ["loadfile", "%s"] }\n' $MEDIA|socat - /tmp/mpvsocket`
* A complete set of commands can be downloaded <a href="https://www.dropbox.com/sh/dnkqk84u16f67gi/AAC55CbOsG-m9Z2-uckskQDHa?dl=0" target="_blank">here</a> and imported as preset
