# Linux Show Player
Linux Show Player (LiSP) - Sound player designed for stage productions

---

Every component on which LiSP relies (python3, GStreamer and Qt5) is multi platform, but the program is currently tested and developed only for **GNU/Linux**.

No special hardware requirements are required to run LiSP, but some processing operations would surely take benefit from a recent CPU.

### Dependencies

*The following names are based on "Arch Linux" packages.*

* python(3) >= 3.4
* python(3)-pyqt5
* python(3)-gobject
* python(3)-setuptools
* qt5-svg
* gstreamer 1.x
* gst-plugins-base
* gst-plugins-good
* gst-plugins-ugly
* gst-plugins-bad
* gst-libav
* portmidi

### Install
  
Download the source archive and extract the files into "linux-show-player", then run:

    easy_install setup.py linux-show-player
