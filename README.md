# Linux Show Player
Linux Show Player (LiSP) - Sound player designed for stage productions

---

Every component on which LiSP relies (python3, GStreamer and Qt5) is multi-platform, but the program is currently tested and developed only for **GNU/Linux**.

No special hardware is required to run LiSP, but some processing operations would surely take benefit from a recent CPU.

### Dependencies

*The following names are based on "Arch Linux" packages.*
<pre>
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
* gst-libav				(optional, for larger format support)
* portmidi				(optional, for portmidi support)
* mido					(installed via pip)
* python-rtmidi			(installed via pip)
* libasound-dev			(if installing in debian/ubuntu)
* libjack-jackd2-dev	(if installing in debian/ubuntu)
</pre>

### Install
  
#####1. Get the source

Download the source archive from GitHub

#####2. Install

	# pip install --pre <archive-name>

for example:
	
	# pip install --pre master.zip

### Usage

Run "linux-show-player"
		