# Linux Show Player [![GitHub release](https://img.shields.io/github/release/FrancescoCeruti/linux-show-player.svg)](https://github.com/FrancescoCeruti/linux-show-player/releases) [![Github Releases](https://img.shields.io/github/downloads/FrancescoCeruti/linux-show-player/total.svg)](https://github.com/FrancescoCeruti/linux-show-player/releases) [![Code Health](https://landscape.io/github/FrancescoCeruti/linux-show-player/master/landscape.svg?style=flat)](https://landscape.io/github/FrancescoCeruti/linux-show-player/master)
Linux Show Player (LiSP) - Sound player designed for stage productions

---

Every component on which LiSP relies (python3, GStreamer and Qt5) is multi-platform, but the program is currently tested and developed only for **GNU/Linux**.

No special hardware is required to run LiSP, but some processing operations would surely take benefit from a recent CPU.

For bugs/requests an issue can be open on the GitHub issues-tracker, any other question can be asked on the [user-group](https://groups.google.com/forum/#!forum/linux-show-player---users).

---

### Installation

####1. Package installation

**For Ubuntu/Debian users:** Follow the instructions on the [releases page](https://github.com/FrancescoCeruti/linux-show-player/releases) on GitHub.

**For ArchLinux users:** there is an AUR package, serch for _linux-show-player_.

####2. Manual Installation

On Debain/Ubuntu and derivates you can build the ".deb" packages, the needed file can be found in _dist/Debian/_

#####2.1 Get the source

Download the archive from the release page on GitHub.

#####2.2 Install (and build) dependencies

**PyPI packages (auto-installed when using pip):**

<pre>
* mido
* python-rtmidi
* JACK-Client
* sortedcontainers
</pre>

**Arch-Linux required packages:**

<pre>
* python
* python-pyqt5
* python-gobject
* python-setuptools
* qt5-svg
* qt5-translations
* gstreamer 1.x
* gst-plugins-base
* gst-plugins-good
* gst-plugins-ugly
* gst-plugins-bad
* gst-libav			(optional, for larger format support)
* portmidi			(optional, for portmidi support)
</pre>

**Debian-based distributions required packages:**

<pre>
* python3
* python3-dev				(build)
* python3-pyqt5
* python3-gi
* python3-setuptools
* python3-pip
* python3-wheel
* libqt5svg5
* libqt5svg5-dev
* qttranslations5-l10n
* gstreamer1.0-plugins-base
* gstreamer1.0-plugins-bad
* gstreamer1.0-plugins-good
* gstreamer1.0-plugins-ugly
* gstreamer1.0-libav
* python3-cffi
* libffi-dev				(build)
* libportmidi-dev			(build)
* libportmidi0
* libasound2-dev			(build)
* asound2
* libjack-jackd2-dev		(build)
* jackd2
</pre>

#####2.3 Install LiSP

    # pip(3) install --pre <archive-name>

for example, to install the latest release from the downloaded zip file:
	
    # pip(3) install --pre linux-show-player-0.3.1.zip

or

    # git clone https://github.com/FrancescoCeruti/linux-show-player
    # pip install --pre linux-show-player/

to install the latest development version from git **(May be unstable and/or contains unfished features)**.

### Usage

Use the installed launcher from the menu (for the package installation), or

    $ linux-show-player                                  # Launch the program
    $ linux-show-player -l [debug/warning/info]          # Launch with different log options
    $ linux-show-player -f <file/path>                   # Open a saved session

*User documentation (in progress) can be found [here](https://github.com/FrancescoCeruti/linux-show-player/wiki)*
