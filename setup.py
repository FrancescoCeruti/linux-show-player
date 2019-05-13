#!/usr/bin/env python3

import os
from pathlib import Path
from setuptools import find_packages, setup

import lisp


def long_description():
    readme = Path(__file__).parent / "README.md"
    with open(readme, encoding="utf8") as readme_file:
        return readme_file.read()


def package_data_dirs(package_path):
    """Fetch all "data" directories in the given package"""
    dirs = []
    for dirpath, dirnames, filenames in os.walk(package_path):
        # Exclude: empty, python-cache and python-modules
        if (
            filenames
            and "__pycache__" not in dirpath
            and "__init__.py" not in filenames
        ):
            rel_dirpath = str(Path(dirpath).relative_to(package_path))
            dirs.append(rel_dirpath + "/*")

    return dirs


# Setup function
setup(
    name="linux-show-player",
    author=lisp.__author__,
    author_email=lisp.__email__,
    version=lisp.__version__,
    license=lisp.__license__,
    url=lisp.__email__,
    description="Cue player for live shows",
    long_description=long_description(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_data={
        "": ["i18n/qm/*", "*.qss", "*.json"],
        "lisp.ui.icons": package_data_dirs("lisp/ui/icons"),
    },
    entry_points={"console_scripts": ["linux-show-player=lisp.main:main"]},
)
