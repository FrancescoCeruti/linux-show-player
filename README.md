# Linux Show Player [![GitHub release](https://img.shields.io/github/release/FrancescoCeruti/linux-show-player.svg?maxAge=2592000)](https://github.com/FrancescoCeruti/linux-show-player/releases) [![Github All Releases](https://img.shields.io/github/downloads/FrancescoCeruti/linux-show-player/total.svg?maxAge=2592000)](https://github.com/FrancescoCeruti/linux-show-player/releases/) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/bef08c3ae14e4953962b7e4bc82a0c03)](https://www.codacy.com/app/ceppofrancy/linux-show-player?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=FrancescoCeruti/linux-show-player&amp;utm_campaign=Badge_Grade) [![Gitter](https://img.shields.io/gitter/room/nwjs/nw.js.svg?maxAge=2592000)](https://gitter.im/linux-show-player/linux-show-player)
Linux Show Player (LiSP) - Sound player designed for stage productions

---

Every component on which LiSP relies (python3, GStreamer and Qt5) is multi-platform, but the program is currently tested and developed only for **GNU/Linux**.

No special hardware is required to run LiSP, but some processing operations would surely take benefit from a recent CPU.

For bugs/requests an issue can be open on the GitHub issues-tracker, for everything else use the [discussions section](https://github.com/FrancescoCeruti/linux-show-player/discussions) or chat on [gitter](https://gitter.im/linux-show-player/linux-show-player).

---

### Installation

#### AppImage

You can download an [AppImage](http://appimage.org/) bundle of LiSP from the release page, once downloaded make the file executable.
Now you should be able to run LiSP by double-clicking the file.

#### Distro Repository

[![Packaging status](https://repology.org/badge/vertical-allrepos/linux-show-player.svg)](https://repology.org/metapackage/linux-show-player)

#### Manually

Otherwise follow the instructions on the [wiki](https://github.com/FrancescoCeruti/linux-show-player/wiki/Install) to install it manually

---

### Usage

Use the installed launcher from the menu (for the package installation), or

    $ linux-show-player                                  # Launch the program
    $ linux-show-player -l [debug/warning/info]          # Launch with different log options
    $ linux-show-player -f <file/path>                   # Open a saved session
    $ linux-show-player --locale <locale>                # Launch using the given locale

*User documentation downloaded under the GitHub release page or [viewed online](http://linux-show-player-users.readthedocs.io/en/latest/index.html)*
