#!/usr/bin/env python3

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Mapping

import toml
from packaging.utils import parse_wheel_filename
from packaging.tags import Tag


def get_best_source(name: str, sources: list, hashes: list):
    # Search for a platform-independent wheel distribution

    for source in sources:
        if (
            source["packagetype"] == "bdist_wheel"
            and source["digests"]["sha256"] in hashes
        ):
            wheel_tags = parse_wheel_filename(source["filename"])[-1]
            if Tag("py3", "none", "any") in wheel_tags:
                return source["url"], source["digests"]["sha256"]

    # Search for a source distribution
    for source in sources:
        if (
            source["packagetype"] == "sdist"
            and "source" in source["python_version"]
            and source["digests"]["sha256"] in hashes
        ):
            return source["url"], source["digests"]["sha256"]

    raise Exception(f"Cannot find a viable distribution for '{name}'.")


def get_pypi_source(name: str, version: str, hashes: list) -> tuple:
    """Get the source information for a dependency."""
    url = f"https://pypi.org/pypi/{name}/json"
    print(f"   Fetching sources for {name} ({version})")

    with urllib.request.urlopen(url) as response:
        body = json.loads(response.read())
        try:
            return get_best_source(name, body["releases"][version], hashes)
        except KeyError:
            raise Exception(f"Failed to extract url and hash from {url}")


def get_package_hashes(package_files: list) -> list:
    regex = re.compile(r"(sha1|sha224|sha384|sha256|sha512|md5):([a-f0-9]+)")
    hashes = []

    for package_file in package_files:
        match = regex.search(package_file["hash"])
        if match:
            hashes.append(match.group(2))

    return hashes


def get_packages_sources(packages: list, parsed_lockfile: Mapping) -> list:
    """Gets the list of sources from a toml parsed lockfile."""
    sources = []
    metadata_files = parsed_lockfile["metadata"].get("files", {})

    executor = ThreadPoolExecutor(max_workers=10)
    futures = []

    for package in packages:
        # Older poetry.lock format contains files in [metadata].
        # New version 2.0 contains files in [[package]] section.
        package_files = metadata_files.get(package["name"], [])
        package_files += package.get("files", [])

        futures.append(
            executor.submit(
                get_pypi_source,
                package["name"],
                package["version"],
                get_package_hashes(package_files),
            )
        )

    for future in as_completed(futures):
        url, hash = future.result()
        sources.append({"type": "file", "url": url, "sha256": hash})

    return sources


def get_locked_packages(parsed_lockfile: Mapping, exclude=tuple()) -> list:
    """Gets the list of dependency names."""
    dependencies = []
    packages = parsed_lockfile.get("package", [])

    for package in packages:
        if (
            package.get("category") == "main"
            and not package.get("optional")
            and package.get("source") is None
            and package.get("name").lower() not in exclude
        ):
            dependencies.append(package)

    return dependencies


def main():
    parser = argparse.ArgumentParser(description="Flatpak Poetry generator")
    parser.add_argument("lockfile")
    parser.add_argument("-e", dest="exclude", default=[], nargs="+")
    parser.add_argument("-o", dest="outfile", default="python-modules.json")
    args = parser.parse_args()

    parsed_lockfile = toml.load(args.lockfile)
    dependencies = get_locked_packages(parsed_lockfile, exclude=args.exclude)
    print(f"Found {len(dependencies)} required packages in {args.lockfile}")

    pip_command = [
        "pip3",
        "install",
        "--no-index",
        "--no-build-isolation",
        '--find-links="file://${PWD}"',
        "--prefix=${FLATPAK_DEST}",
        " ".join([d["name"] for d in dependencies]),
    ]
    main_module = OrderedDict(
        [
            ("name", "python-modules"),
            ("buildsystem", "simple"),
            ("build-commands", [" ".join(pip_command)]),
        ]
    )

    print("Fetching metadata from pypi")
    sources = get_packages_sources(dependencies, parsed_lockfile)
    main_module["sources"] = sources

    print(f'Writing modules to "{args.outfile}"')
    with open(args.outfile, "w") as f:
        f.write(json.dumps(main_module, indent=4))

    print("Done!")


if __name__ == "__main__":
    main()
