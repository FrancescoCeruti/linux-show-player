#!/usr/bin/env bash

export FLATPAK_RUNTIME="org.kde.Platform"
export FLATPAK_RUNTIME_VERSION="5.15-22.08"
export FLATPAK_SDK="org.kde.Sdk"

export FLATPAK_INSTALL="$FLATPAK_RUNTIME//$FLATPAK_RUNTIME_VERSION $FLATPAK_SDK//$FLATPAK_RUNTIME_VERSION"

export FLATPAK_PY_LOCKFILE="../../poetry.lock"
# Python packages included in the runtime sdk (some are not included in the runtime)
export FLATPAK_PY_INCLUDED="cython mako markdown meson pip pygments setuptools six wheel"
# Python packages to ignore
export FLATPAK_PY_IGNORE="$FLATPAK_PY_INCLUDED pygobject pycairo pyqt5 pyqt5-sip pyqt5-qt pyqt5-qt5"

export FLATPAK_APP_ID="org.linux_show_player.LinuxShowPlayer"
export FLATPAK_APP_MODULE="linux-show-player"