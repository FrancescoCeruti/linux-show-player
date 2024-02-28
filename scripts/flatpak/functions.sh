#!/usr/bin/env bash

source config.sh

function flatpak_build_manifest() {
    # Create virtual-environment
    python3 -m venv ./venv

    # Install requirements
    source ./venv/bin/activate
    pip3 install --upgrade -r requirements.txt

    # Build manifest
    python3 patch-manifest.py
    python3 poetry-flatpak.py "$FLATPAK_PY_LOCKFILE" -e $FLATPAK_PY_IGNORE
    deactivate
}

function flatpak_install_runtime() {
    echo ""
    echo "######################################"
    echo "#    Add flatpak remote (flathub)    #"
    echo "######################################"
    echo ""

    flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
}

function flatpak_build() {
    echo ""
    echo "###########################"
    echo "#    Build the flatpak    #"
    echo "###########################"
    echo ""

    # Prepare the repository
    ostree init --mode=archive-z2 --repo=repo
    # Build the flatpak
    flatpak-builder --verbose --force-clean --ccache --repo=repo --user --install-deps-from=flathub build $FLATPAK_APP_ID.json
}


function flatpak_build_noexit() {
    if  [[ ${-/e} != $- ]] ; then set +e ; USE_E=1 ; else USE_E=0 ; fi

    flatpak_build
    echo "$?" > "FB_EXIT_CODE"

    if [[ $USE_E -eq 1 ]] ; then set -e ; fi
}

function flatpak_build_noexit_check() {
    if [[ -f "FB_EXIT_CODE" ]] ; then
        if [[ $(cat "FB_EXIT_CODE") -ne 0 ]] ; then
            >&2 echo "Error: flatpak-builder exit with non-zero"
            exit $(cat "FB_EXIT_CODE")
        fi
    fi
}

function flatpak_bundle() {
    echo ""
    echo "###############################"
    echo "#    Create flatpak bundle    #"
    echo "###############################"
    echo ""

    mkdir -p out
    # Create the bundle (without blocking the script)
    flatpak build-bundle repo out/linux-show-player.flatpak $FLATPAK_APP_ID $BUILD_BRANCH &
    # Print elapsed time
    watch_process $!
}

function watch_process() {
    elapsed="00:00"
    # If this command is killed, kill the watched process
    trap "kill $1 2> /dev/null" EXIT
    # While the process is running print the elapsed time every second
    while kill -0 $1 2> /dev/null; do
        elapsed=$(echo -en $(ps -o etime= -p "$1"))
        echo -ne "[ $elapsed ] Building ...\r"
        sleep 1
    done
    # Print a "completed message"
    echo "Completed in $elapsed                                  "
    # Disable the trap on a normal exit.
    trap - EXIT
}
