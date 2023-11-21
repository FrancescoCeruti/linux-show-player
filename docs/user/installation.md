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
 * [Master](https://github.com/FrancescoCeruti/linux-show-player/releases/tag/ci-master) - Generally stable
 * [Development](https://github.com/FrancescoCeruti/linux-show-player/releases/tag/ci-develop) - Preview features, might be unstable and untested

### Install

If you have the right app installed it might be possible to simply double-click the downloaded file, otherwise, you
can use the following command:

```shell
flatpak install "path/to/file.flatpak"
```

---

## 🐧 From your distribution repository

For some GNU/Linux distributions you can install a native package.<br>
Keeping in mind that it might not be the latest version, you can find a list on <a href="https://repology.org/metapackage/linux-show-player" target="_blank">repology.org</a>.

---

## 🛠️ Manually

```{note}
What follows are general guidelines, to run LiSP without a "proper" installation.
```

### Distribution dependencies

You should install these libraries/packages using your package manager:

- python
- python-poetry (>= 1.2, otherwise follow <a href="https://python-poetry.org/docs/#installation" target="_blank">these instructions</a>)
- gstreamer
- gstreamer-plugins-(good/ugly/bad)
- gstreamer-libav (for larger format support)
- alsa-lib (with development files)
- rtmidi (with development files)
- liblo (with development files)

```{note}
Some dependencies will be installed via poetry. If you need a full list, check the `pyproject.toml` file.
```

```{note}
You might also need to install `ola`, for ArtNet timecode.
However, using the method described below, it's not possile to use it. 
```

### Download

Download the source code from GitHub or clone the git repository.

### Run

You can run it locally via:

```shell
cd "source/code/root"

poetry install

poetry run linux-show-player
```