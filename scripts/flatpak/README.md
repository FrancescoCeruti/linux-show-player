### INTRO

(╯°□°)╯︵ ┻━┻

The scripts in this folder allow to build a Flatpak package of Linux Show Player.

 * **build_flatpak.sh:** Combine the commands from "functions.sh" to run a complete build
 * **config.sh:** Some environment configuration
 * **functions.sh:** A collection of commands to build the flatpak
 * **patch-flatpak.py:** Patch the flatpak manifest to use the current CI branch/commit
 * **poetry-flatpak.py:** Starting from the project poetry.lock generate the appropriate modules to install the python requirements
 * **pyqt-build.sh:** Used to invoke "sip-install" to build pyqt

### REQUIREMENTS

 * ostree
 * flatpak >= 1.0
 * flatpak-builder
 * python >= 3.6
   * packaging
   * toml
 * the BUILD_BRANCH variable to be set.

### NOTES

Non-used features of the various packages should be disabled when possible.
