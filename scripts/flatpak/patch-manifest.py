import json
import os

app_branch = os.environ["BUILD_BRANCH"]
app_id = os.environ["FLATPAK_APP_ID"]
app_module = os.environ["FLATPAK_APP_MODULE"]

current_dir = os.path.dirname(__file__)
manifest_path = os.path.join(current_dir, app_id + ".json")

print("Patching flatpak manifest")
with open(manifest_path, mode="r") as f:
    manifest = json.load(f)

# Patch top-level attributes
manifest["branch"] = app_branch
if app_branch != "master":
    manifest["desktop-file-name-suffix"] = " ({})".format(app_branch)

# Patch the app-module to use the correct branch
for module in manifest["modules"]:
    if isinstance(module, dict) and module["name"] == app_module:
        module["sources"][0]["branch"] = app_branch
        break

# Save the patched manifest
with open(manifest_path, mode="w") as f:
    json.dump(manifest, f, indent=4)

print("Done!")
