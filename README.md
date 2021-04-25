<p align="center">
    <img src="https://github.com/FrancescoCeruti/linux-show-player/blob/develop/dist/linuxshowplayer.png?raw=true" alt="Logo" width="100" height=100>
</p>
<h1 align="center">Linux Show Player</h1>
<h3 align="center">Cue player for stage productions</h3>

<p align="center">
    <a href="https://github.com/FrancescoCeruti/linux-show-player/blob/master/LICENSE"><img alt="License: GPL" src="https://img.shields.io/badge/license-GPL-blue.svg"></a>
    <a href="https://github.com/FrancescoCeruti/linux-show-player/releases/latest"><img src="https://img.shields.io/github/release/FrancescoCeruti/linux-show-player.svg?maxAge=2592000" alt="GitHub release" /></a>
    <a href="https://github.com/FrancescoCeruti/linux-show-player/releases"><img src="https://img.shields.io/github/downloads/FrancescoCeruti/linux-show-player/total.svg?maxAge=2592000" alt="Github All Releases" /></a>
    <a href="https://www.codacy.com/app/ceppofrancy/linux-show-player?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=FrancescoCeruti/linux-show-player&amp;utm_campaign=Badge_Grade"><img src="https://api.codacy.com/project/badge/Grade/bef08c3ae14e4953962b7e4bc82a0c03" alt="Code Health" /></a>
    <a href="https://gitter.im/linux-show-player/linux-show-player"><img src="https://img.shields.io/gitter/room/nwjs/nw.js.svg?maxAge=2592000" alt="Gitter" /></a>
    <a href="https://github.com/ambv/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black"></a>
</p>

---

Linux Show Player, LiSP for short, is a free cue player, mainly intended for sound-playback in stage productions, the goal is to provide a complete playback software for musical plays, theater shows and similar.

For bugs/requests you can open an issue on the GitHub issues tracker, for support, discussions, and anything else you should use the [gitter](https://gitter.im/linux-show-player/linux-show-player) chat.

---

### Installation

Linux Show Player is currently developed/test only on **GNU/Linux**.<br>
_The core components (Python3, GStreamer and Qt5) are multi-platform, in future, despite the name, LiSP might get ported on others platforms_

#### 📦 Flatpak

From version _0.6_ it will be possible to install a [Flatpak](https://flatpak.org/) package, follow the _simple_ instructions on their website to get everything ready. 

You can get the latest **development** builds here:
 * [Master](https://github.com/FrancescoCeruti/linux-show-player/releases/tag/ci-master) - Generally stable
 * [Development](https://github.com/FrancescoCeruti/linux-show-player/releases/tag/ci-develop) - Preview features, might be unstable and untested

#### 🐧 From yours distribution repository

For some GNU/Linux distribution you can install a native package.<br>
Keep in mind that it might not be the latest version, you can find a list on [repology.org](https://repology.org/metapackage/linux-show-player)

---

### 📖 Usage

User manual can be [viewed online](http://linux-show-player-users.readthedocs.io/en/latest/index.html)
or downloaded from the GitHub release page, for a specific version.

#### ⌨️ Command line:

```
usage: linux-show-player [-h] [-f [FILE]] [-l {debug,info,warning}]
                         [--locale LOCALE]

Cue player for stage productions.

optional arguments:
  -h, --help            show this help message and exit
  -f [FILE], --file [FILE]
                        Session file to open
  -l {debug,info,warning}, --log {debug,info,warning}
                        Change output verbosity. default: warning
  --locale LOCALE       Force specified locale/language
```
