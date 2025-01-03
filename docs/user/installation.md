# Installation

There are multiple ways to get LiSP installed in your system.

## 📦 Flatpak

This is usually the easy path, but depending on your needs it might not be the best.

```{note}
- Native JACK is not support in flatpaks, you can get JACK working via PipeWire (pipewire-jack)
- You might get some issues with dialogs placement and window decorations in Wayland sessions
```

### Prepare your system

If you don't already have flatpak installed,
follow their _simple_ instructions, <a href="https://flatpak.org/setup/" target="_blank">here</a>. 

### Download LiSP

You can get the latest builds here:

 * [Flathub](https://flathub.org/apps/org.linuxshowplayer.LinuxShowPlayer) - Official release
 * [Master](https://github.com/FrancescoCeruti/linux-show-player/releases/tag/ci-master) - Generally stable
 * [Development](https://github.com/FrancescoCeruti/linux-show-player/releases/tag/ci-develop) - Preview features, might be unstable and untested

### Install (master/development)

If you have the right app installed it might be possible to simply double-click the downloaded file, otherwise, you
can use the following command:

```shell
flatpak install "path/to/file.flatpak"
```

```{important}
**If the installation produce an error similar the this:**
 
`The application org.linuxshowplayer.LinuxShowPlayer/x86_64/master requires the runtime org.kde.Platform/x86_64/5.15-23.08 which was not found.`

**Before installing LiSP you need to run the following:**

`flatpak install <name-of-the-runtime>`

In the above example the runtime name is `org.kde.Platform/x86_64/5.15-23.08`.
```

---

## 🐧 From your distribution repository

For some GNU/Linux distributions you can install a native package.<br>
Keeping in mind that it might not be the latest version, you can find a list on <a href="https://repology.org/metapackage/linux-show-player" target="_blank">repology.org</a>.

---

## 🛠️ Manually

You want to test something? Hack some plugin? Or simply none of the options above satisfy your needs?
Then you can install LiSP manually.

With the following instructions you will:

 1. Install binary dependencies from your distribution repository
 2. Install python dependencies (from <a href="https://pypi.org/" target="_blank">pypi</a>) in a venv managed by <a href="https://python-poetry.org/" target="_blank">poetry</a>
 3. Run LiSP in that venv via poetry

```{important}
What follows are guidelines to run LiSP without a "proper" installation, **if something is missing or doesn't work let us know!**
```

### Dependencies (1/2)

To start, you'll need to install these packages using your package manager:

```{tab} Debian/Ubuntu/Mint
 * `python3` (>= 3.8)
 * `python3-dev`
 * `python3-poetry` (>= 1.2, otherwise follow <a href="https://python-poetry.org/docs/#installation" target="_blank">these instructions</a>)
 * `gstreamer1.0-plugins-good`
 * `gstreamer1.0-plugins-ugly`
 * `gstreamer1.0-plugins-bad`
 * `gstreamer1.0-libav`
 * `libasound2`
 * `libasound2-dev`
 * `libgirepository1.0-dev`
 * `libcairo2-dev`
 * `librtmidi6`
```

```{tab} Fedora/CentOS
 * `python3` (>= 3.8)
 * `python3-devel`
 * `poetry` (>= 1.2, otherwise follow <a href="https://python-poetry.org/docs/#installation" target="_blank">these instructions</a>)
 * `gstreamer1-plugins-good`
 * `gstreamer1-plugins-ugly-free`
 * `gstreamer1-plugins-bad-free`
 * `gstreamer1-plugin-libav` (Not available on CentOS)
 * `alsa-lib`
 * `alsa-lib-devel`
 * `gobject-introspection-devel`
 * `cairo-gobject-devel`
 * `rtmidi`
```

```{tab} ArchLinux
 * `python`
 * `python-poetry`
 * `gst-plugins-good`
 * `gst-plugins-ugly`
 * `gst-plugins-bad`
 * `gst-libav`
 * `alsa-lib`
 * `cairo`
 * `gobject-introspection`
 * `rtmidi`
```

```{tab} Gentoo
 * `python`
 * `poetry`
 * `gst-plugins-good`
 * `gst-plugins-ugly`
 * `gst-plugins-bad`
 * `gst-plugins-libav`
 * `alsa-lib`
 * `cairo`
 * `gobject-introspection`
 * `rtmidi`
```

```{hint}
You might also want to install `ola`, for ArtNet timecode, however, using the method described here, it's not possile to use it. 
```

### Download

Download the source code from <a href="https://github.com/FrancescoCeruti/linux-show-player" target="_blank">GitHub</a> or clone the git repository.

### Dependencies (2/2)

Install the python dependencies:

```shell
# From the source code root
poetry install
```

```{note}
Run this step every time you download a new version of the code.
```

### Run

```shell
# From the source code root
poetry run linux-show-player
```
