![Linux Show Player Logo](https://raw.githubusercontent.com/wiki/FrancescoCeruti/linux-show-player/media/site_logo.png)
<h3 align="center"> Cue player designed for stage productions</h3>

<p align="center">
<a href="https://github.com/FrancescoCeruti/linux-show-player/blob/master/LICENSE"><img alt="License: GPL" src="https://img.shields.io/badge/license-GPL-blue.svg"></a>
<a href="https://github.com/FrancescoCeruti/linux-show-player/releases/latest"><img src="https://img.shields.io/github/release/FrancescoCeruti/linux-show-player.svg?maxAge=2592000" alt="GitHub release" /></a>
<a href="https://github.com/FrancescoCeruti/linux-show-player/releases"><img src="https://img.shields.io/github/downloads/FrancescoCeruti/linux-show-player/total.svg?maxAge=2592000" alt="Github All Releases" /></a>
<a href="https://www.codacy.com/app/ceppofrancy/linux-show-player?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=FrancescoCeruti/linux-show-player&amp;utm_campaign=Badge_Grade"><img src="https://api.codacy.com/project/badge/Grade/bef08c3ae14e4953962b7e4bc82a0c03" alt="Code Health" /></a>
<a href="https://gitter.im/linux-show-player/linux-show-player"><img src="https://img.shields.io/gitter/room/nwjs/nw.js.svg?maxAge=2592000" alt="Gitter" /></a>
<a href="https://github.com/ambv/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black"></a>
<a href="https://saythanks.io/to/FrancescoCeruti"><img src="https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg" alt="Say Thanks!"></a>
</p>

---

Every component on which LiSP relies (python3, GStreamer and Qt5) is multi-platform, but the program is currently tested and developed only for **GNU/Linux**.

No special hardware is required to run LiSP, but some processing operations would surely take benefit from a recent CPU.

For bugs/requests an issue can be open on the GitHub issues-tracker, for everything else [gitter](https://gitter.im/linux-show-player/linux-show-player) can be used.

---

### Installation

You can download an [AppImage](http://appimage.org/) bundle of LiSP from the release page, once downloaded make the file executable.
Now you should be able to run LiSP by double-clicking the file.

Tested on the following systems *(it should work on newer versions)*:
 * Debian 8
 * Ubuntu 16.04
 * Fedora 24

<br />Otherwise follow the instructions on the [wiki](https://github.com/FrancescoCeruti/linux-show-player/wiki/Install) 

---

### Usage

Use the installed launcher from the menu, or:

    $ linux-show-player                                  # Launch the program
    $ linux-show-player -l [debug/warning/info]          # Launch with different log options
    $ linux-show-player -f <file/path>                   # Open a saved session
    $ linux-show-player --locale <locale>                # Launch using the given locale

User documentation can be downloaded under the GitHub release page or [viewed online](http://linux-show-player-users.readthedocs.io/en/latest/index.html)