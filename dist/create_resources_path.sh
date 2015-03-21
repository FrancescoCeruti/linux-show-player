#!/bin/bash

appdir="./usr/share/applications"
mimedir="./usr/share/mime/packages"
pixdir="./usr/share/pixmaps"

# Make applications directory and copy the .desktop file
mkdir -p $appdir
cp "linux-show-player.desktop" $appdir

# Make mime directory and copy the specification file
mkdir -p $mimedir
cp "linux-show-player.xml" $mimedir

# Make the pixmaps directory and copy the icons
mkdir -p $pixdir
cp "linux_show_player.png" $pixdir
cp "application-x-linuxshowplayer.png" "$pixdir"
