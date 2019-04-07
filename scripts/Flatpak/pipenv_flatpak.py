import html5lib
import json
import os
import requests
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, wait

# From pip project (https://github.com/pypa/pip)
BZ2_EXTENSIONS = (".tar.bz2", ".tbz")
XZ_EXTENSIONS = (".tar.xz", ".txz", ".tlz", ".tar.lz", ".tar.lzma")
ZIP_EXTENSIONS = (".zip", ".whl")
TAR_EXTENSIONS = (".tar.gz", ".tgz", ".tar")
ARCHIVE_EXTENSIONS = (
    ZIP_EXTENSIONS + BZ2_EXTENSIONS + TAR_EXTENSIONS + XZ_EXTENSIONS
)

PLATFORMS_LINUX_x86_64 = ("linux_x86_64", "manylinux1_x86_64", "any")
PYPI_URL = "https://pypi.python.org/simple/"


def _flatpak_module_template():
    return {
        "name": "",
        "buildsystem": "simple",
        "build-commands": [
            "pip3 --verbose install --no-index --no-deps --ignore-installed --no-build-isolation --prefix=${FLATPAK_DEST} "
        ],
        "sources": [{"type": "file", "url": "", "sha256": ""}],
    }


def _is_like_archive(filename):
    """Return whether the filename looks like an archive."""
    for ext in ARCHIVE_EXTENSIONS:
        if filename.endswith(ext):
            return True, ext

    return False, None


def _is_wheel(filename):
    if filename.endswith(".whl"):
        return True

    return False


def _wheel_versions(py_version):
    return {
        "py" + py_version.replace(".", ""),
        "py" + py_version[0],
        "cp" + py_version.replace(".", ""),
    }


def _wheel_tags(filename):
    """Get wheel tags from the filename, see pep-0425

    Returns:
        A tuple (version, set(python-tags), platform-tag)
    """
    parts = filename[:-4].split("-")
    return parts[1], set(parts[-3].split(".")), parts[-1]


def _find_candidate_downloads(package, whl_platforms, whl_versions):
    for filename, url in package["candidates"]:
        if _is_wheel(filename):
            if package["wheel"] is not None:
                # Take the first matching wheel, ignore others
                continue

            version, python_tags, platform_tag = _wheel_tags(filename)
            if version != package["version"]:
                # print('  discard version {}'.format(version))
                continue
            if platform_tag not in whl_platforms:
                # print('  discard platform {}'.format(platform_tag))
                continue
            if not python_tags.intersection(whl_versions):
                # print('  discard python-version {}'.format(python_tags))
                continue

            url, fragment = urllib.parse.urldefrag(url)
            if not fragment.startswith("sha256="):
                continue

            package["wheel"] = (url, fragment[7:])
            if package["source"] is not None:
                break
        else:
            is_archive, ext = _is_like_archive(filename)
            if is_archive:
                version = filename[: -(len(ext))].split("-")[-1]
                if version != package["version"]:
                    # print('  discard version {}'.format(version))
                    continue

                url, fragment = urllib.parse.urldefrag(url)
                if not fragment.startswith("sha256="):
                    continue

                package["source"] = (url, fragment[7:])
                if package["wheel"] is not None:
                    break


def get_locked_packages(lock_file):
    with open(lock_file, mode="r") as lf:
        lock_content = json.load(lf)

    # Get the required packages
    packages = []
    for name, info in lock_content.get("default", {}).items():
        packages.append(
            {
                "name": name,
                "version": info["version"][2:],
                "candidates": [],
                "wheel": None,
                "source": None,
            }
        )

    return packages


def fetch_downloads_candidates(url_template, packages):
    session = requests.session()

    def fetch(package):
        print("   Download candidates for {}".format(package["name"]))

        # GET the page from the mirror
        url = url_template.format(package["name"])
        resp = session.get(url)

        if resp.status_code != 200:
            print(
                "   Cannot fetch candidates: error {}".format(resp.status_code)
            )

        # Parse HTML content
        html = html5lib.parse(resp.content, namespaceHTMLElements=False)

        # Iterate all the provided downloads
        for link in html.findall(".//a"):
            package["candidates"].append((link.text, link.attrib["href"]))

    with ThreadPoolExecutor(max_workers=10) as executor:
        wait(tuple(executor.submit(fetch, package) for package in packages))

    session.close()


def filter_candidates(packages, whl_platforms, whl_versions):
    for package in packages:
        _find_candidate_downloads(package, whl_platforms, whl_versions)
        # Cleanup
        package.pop("candidates")


def generate(lock_file, py_version, platforms, base_url):
    # Read the Pipfile.lock
    print("=> Reading Pipfile.lock ...")
    packages = get_locked_packages(lock_file)
    print("=> Found {} required packages".format(len(packages)))
    print("=> Fetching packages info from {}".format(base_url))
    fetch_downloads_candidates(base_url + "{}/", packages)
    print("=> Filtering packages downloads candidates ...")
    filter_candidates(packages, platforms, _wheel_versions(py_version))

    # Insert python-packages modules
    for package in packages:
        if package["wheel"] is not None:
            source = package["wheel"]
        elif package["source"] is not None:
            source = package["source"]
        else:
            print("   Skip: {}".format(package["name"]))
            continue

        print("   Selected: {}".format(source[0]))

        module = _flatpak_module_template()
        module["name"] = package["name"]
        module["build-commands"][0] += os.path.basename(
            urllib.parse.urlsplit(source[0]).path
        )
        module["sources"][0]["url"] = source[0]
        module["sources"][0]["sha256"] = source[1]

        yield module


if __name__ == "__main__":
    import pprint
    import platform

    for module in tuple(
        generate(
            "../../Pipfile.lock",
            ".".join(platform.python_version_tuple[:2]),
            PLATFORMS_LINUX_x86_64,
            PYPI_URL,
        )
    ):
        pprint.pprint(module, indent=4, width=1000)
