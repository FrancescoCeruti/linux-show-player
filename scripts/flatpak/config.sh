#!/usr/bin/env bash

export FLATPAK_RUNTIME="org.kde.Platform"
export FLATPAK_RUNTIME_VERSION="6.7"
export FLATPAK_SDK="org.kde.Sdk"

export FLATPAK_INSTALL="$FLATPAK_RUNTIME//$FLATPAK_RUNTIME_VERSION $FLATPAK_SDK//$FLATPAK_RUNTIME_VERSION"

export FLATPAK_PY_LOCKFILE="../../poetry.lock"
# Python packages included in the runtime sdk (some are not included in the runtime)
export FLATPAK_PY_INCLUDED="cython mako markdown meson pip pygments setuptools six wheel"
# Python packages to ignore
export FLATPAK_PY_IGNORE="$FLATPAK_PY_INCLUDED packaging pyalsa pyliblo3 python-rtmidi pygobject pycairo pyqt6 pyqt6-sip pyqt6-qt pyqt6-qt6 numpy"

export FLATPAK_APP_ID="org.linuxshowplayer.LinuxShowPlayer"
export FLATPAK_APP_MODULE="linux-show-player"