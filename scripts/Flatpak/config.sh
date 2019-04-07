#!/usr/bin/env bash

export FLATPAK_RUNTIME="org.gnome.Platform"
export FLATPAK_RUNTIME_VERSION="3.32"
export FLATPAK_SDK="org.gnome.Sdk"

export FLATPAK_INSTALL="$FLATPAK_RUNTIME//$FLATPAK_RUNTIME_VERSION $FLATPAK_SDK//$FLATPAK_RUNTIME_VERSION"

export FLATPAK_PY_VERSION="3.7"
export FLATPAK_PY_IGNORE_PACKAGES="setuptools six pygobject pycairo pyqt5 sip"

export FLATPAK_APP_ID="com.github.FrancescoCeruti.LinuxShowPlayer"
export FLATPAK_APP_MODULE="linux-show-player"