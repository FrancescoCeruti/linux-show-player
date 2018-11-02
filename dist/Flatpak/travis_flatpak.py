import json
import urllib.parse
import os

import pipenv_flatpak

DIR = os.path.dirname(__file__)
BRANCH = os.environ["TRAVIS_BRANCH"]
COMMIT = os.environ["TRAVIS_COMMIT"]

APP_ID = "com.github.FrancescoCeruti.LinuxShowPlayer"
APP_MODULE = "linux-show-player"
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

py_version = None
app_index = None

# Get python version "major.minor" and patch the app-module to use the correct
# branch
for index, module in enumerate(manifest["modules"]):
    if module["name"] == "cpython":
        path = urllib.parse.urlsplit(module["sources"][0]["url"]).path
        file = os.path.basename(path)
        py_version = file[2:5]
    elif module["name"] == APP_MODULE:
        module["sources"][0]["branch"] = BRANCH
        module["sources"][0]["commit"] = COMMIT
        app_index = index

# Generate python-modules from Pipfile.lock, insert them before the app-module
for num, py_module in enumerate(
    pipenv_flatpak.generate(
        LOCKFILE,
        py_version,
        pipenv_flatpak.PLATFORMS_LINUX_x86_64,
        pipenv_flatpak.PYPI_URL,
    )
):
    manifest["modules"].insert((app_index - 1) + num, py_module)

# Save the patched manifest
with open(DESTINATION, mode="w") as out:
    json.dump(manifest, out, indent=4)

print("\n>>> Done!")
