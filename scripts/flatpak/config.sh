#!/usr/bin/env bash

export FLATPAK_RUNTIME="org.gnome.Platform"
export FLATPAK_RUNTIME_VERSION="3.38"
export FLATPAK_SDK="org.gnome.Sdk"

export FLATPAK_INSTALL="$FLATPAK_RUNTIME//$FLATPAK_RUNTIME_VERSION $FLATPAK_SDK//$FLATPAK_RUNTIME_VERSION"

export FLATPAK_PY_LOCKFILE="../../poetry.lock"
export FLATPAK_PY_IGNORE_PACKAGES="pygobject pycairo pyqt5 pyqt5-sip pyqt5-qt pyqt5-qt5"

export FLATPAK_APP_ID="org.linux_show_player.LinuxShowPlayer"
export FLATPAK_APP_MODULE="linux-show-player"