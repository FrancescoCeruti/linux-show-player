#!/usr/bin/env bash

# Exit script if a statement returns a non-true return value.
set -o errexit
# Use the error status of the first failure, rather than that of the last item in a pipeline.
set -o pipefail

echo ""
echo "================= build-flatpak.sh ================="
echo ""

# Make sure we are in the same directory of this file
cd "${0%/*}"

# Load Environment variables
source functions.sh

# Print relevant variables
echo "<<< FLATPAK_INSTALL = "$FLATPAK_INSTALL
echo "<<< FLATPAK_APP_ID = " $FLATPAK_APP_ID
echo "<<< FLATPAK_APP_MODULE = " $FLATPAK_APP_MODULE

flatpak_install_runtime
flatpak_build_manifest
flatpak_build
flatpak_bundle

echo ""
echo "================= build-flatpak.sh ================="
echo ""