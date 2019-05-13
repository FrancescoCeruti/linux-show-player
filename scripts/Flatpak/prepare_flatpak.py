import json
import os

import pipenv_flatpak

BRANCH = os.environ["BUILD_BRANCH"]
APP_ID = os.environ["FLATPAK_APP_ID"]
PY_VERSION = os.environ["FLATPAK_PY_VERSION"]
APP_MODULE = os.environ["FLATPAK_APP_MODULE"]
IGNORE_PACKAGES = [
    p.lower() for p in os.environ.get("FLATPAK_PY_IGNORE_PACKAGES", "").split()
]

DIR = os.path.dirname(__file__)
TEMPLATE = os.path.join(DIR, "template.json")
DESTINATION = os.path.join(DIR, APP_ID + ".json")
LOCKFILE = "../../Pipfile.lock"

print(">>> Generating flatpak manifest ....\n")
with open(TEMPLATE, mode="r") as f:
    manifest = json.load(f)

# Patch top-Level attributes
manifest["branch"] = BRANCH
if BRANCH != "master":
    manifest["desktop-file-name-suffix"] = " ({})".format(BRANCH)

# Patch the app-module to use the correct branch
app_index = 0
for index, module in enumerate(manifest["modules"]):
    if module["name"] == APP_MODULE:
        app_index = index
        module["sources"][0]["branch"] = BRANCH
        break

# Generate python-modules from Pipfile.lock, insert them before the app-module
for num, py_module in enumerate(
    pipenv_flatpak.generate(
        LOCKFILE,
        PY_VERSION,
        pipenv_flatpak.PLATFORMS_LINUX_x86_64,
        pipenv_flatpak.PYPI_URL,
    )
):
    if py_module["name"].lower() not in IGNORE_PACKAGES:
        manifest["modules"].insert((app_index - 1) + num, py_module)
    else:
        print("=> Package ignored: {}".format(py_module["name"]))

# Save the patched manifest
with open(DESTINATION, mode="w") as out:
    json.dump(manifest, out, indent=4)

print("\n>>> Done!")
