#!/bin/bash

# Make sure we are in the same directory of this file
cd "${0%/*}"
# Include some travis utility function
source "functions.sh"

BRANCH="$1"

set -e

# Prepare the repository
ostree init --mode=archive-z2 --repo=repo

# Install runtime and sdk
travis_fold start "flatpak_install_deps"
    travis_time_start
        flatpak --user remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
        flatpak --user install flathub org.gnome.Platform//3.28 org.gnome.Sdk//3.28
    travis_time_finish
travis_fold end "flatpak_install_deps"
echo -e \\n

# Build
travis_fold start "flatpak_build"
    travis_time_start
        flatpak-builder --verbose --force-clean --ccache --repo=repo \
                        build com.github.FrancescoCeruti.LinuxShowPlayer.json
    travis_time_finish
travis_fold end "flatpak_build"
echo -e \\n

# Bundle the build
travis_fold start "flatpak_bundle"
    travis_time_start
        mkdir -p out
        flatpak build-bundle --verbose repo out/LinuxShowPlayer.flatpak \
                com.github.FrancescoCeruti.LinuxShowPlayer $BRANCH
    travis_time_finish
travis_fold end "flatpak_update_repo"
echo -e \\n

set +e