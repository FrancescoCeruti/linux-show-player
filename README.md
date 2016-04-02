# Linux Show Player [![GitHub release](https://img.shields.io/github/release/FrancescoCeruti/linux-show-player.svg)](https://github.com/FrancescoCeruti/linux-show-player/releases) [![Github Releases](https://img.shields.io/github/downloads/FrancescoCeruti/linux-show-player/total.svg)](https://github.com/FrancescoCeruti/linux-show-player/releases) [![Code Health](https://landscape.io/github/FrancescoCeruti/linux-show-player/master/landscape.svg?style=flat)](https://landscape.io/github/FrancescoCeruti/linux-show-player/master) [![Code Issues](https://www.quantifiedcode.com/api/v1/project/c419c19d00ce403a82f16a4505161e49/badge.svg)](https://www.quantifiedcode.com/app/project/c419c19d00ce403a82f16a4505161e49)
Linux Show Player (LiSP) - Sound player designed for stage productions

---

Every component on which LiSP relies (python3, GStreamer and Qt5) is multi-platform, but the program is currently tested and developed only for **GNU/Linux**.

No special hardware is required to run LiSP, but some processing operations would surely take benefit from a recent CPU.

For bugs/requests an issue can be open on the GitHub issues-tracker, any other question can be asked on the [user-group](https://groups.google.com/forum/#!forum/linux-show-player---users).

---

### Installation

####1. Package installation

**For Ubuntu/Debian users:** Download the ".deb" package in the releases page on GitHub (only tested on Ubuntu).

**For ArchLinux users:** there is an AUR Package.

####2. Manual Installation

#####2.1 Get the source

Download the archive from the release page on GitHub.

#####2.2 Install dependencies

*The following names are based on "Arch Linux" packages.*
<pre>
* python(3) >= 3.4
* python(3)-pyqt5
* python(3)-gobject
* python(3)-setuptools
* qt5-svg
* gstreamer 1.x
* gst-plugins-base      (gstreamer1.0-plugins-base in debian)
* gst-plugins-good      (gstreamer1.0-plugins-good in debian)
* gst-plugins-ugly      (gstreamer1.0-plugins-ugly in debian)
* gst-plugins-bad       (gstreamer1.0-plugins-bad in debian)
* libffi-dev            (if installing in debian/ubuntu)
* gst-libav				(optional, for larger format support)
* portmidi				(optional, for portmidi support)
* mido					(auto-installed via pip)
* python-rtmidi			(auto-installed via pip)
* JACK-Client			(auto-installed via pip)
* sortedcontainers      (auto-installed via pip)
* libasound2-dev	    (if installing in debian/ubuntu)
* libjack-jackd2-dev	(if installing in debian/ubuntu)
</pre>

#####2.3 Install LiSP

    # pip(3) install --pre <archive-name>

for example, to install the latest release from the downloaded zip file:
	
    # pip(3) install --pre linux-show-player-0.3.1.zip

or

    # git clone https://github.com/FrancescoCeruti/linux-show-player
    # pip install --pre linux-show-player/

to install the latest development version from git.

### Usage

Use the installed launcher from the menu (for the package installation), or

    $ linux-show-player                                  # Launch the program
    $ linux-show-player -l [debug/warning/info]          # Launch with different log options
    $ linux-show-player -f <file/path>                   # Open a saved session

*Currently no user documentation is available.*
