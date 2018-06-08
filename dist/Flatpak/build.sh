#!/bin/sh

# Make sure we are in the same directory of this file
cd "${0%/*}"
BRANCH="$1"

set -xe

# Create and add a local repository
ostree init --mode=archive-z2 --repo=repository
flatpak remote-add --user --no-gpg-verify --if-not-exists repo repository

# Install runtime and sdk
flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install --user flathub org.gnome.Platform//3.28 org.gnome.Sdk//3.28

# Run the build
flatpak-builder --verbose --force-clean --ccache --repo=repo build com.github.FrancescoCeruti.LinuxShowPlayer.json

# Bundle
mkdir -p out
flatpak build-bundle repo out/LinuxShowPlayer.flatpak com.github.FrancescoCeruti.LinuxShowPlayer $BRANCH

set +xe