#!/usr/bin/env python3
#
# This file is part of Linux Show Player
#
# Copyright 2018 Francesco Ceruti <ceppofrancy@gmail.com>
#
# Linux Show Player is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Linux Show Player is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Linux Show Player.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import os
import sys
from shutil import copyfile

from lisp.core.loading import module_to_class_name

parser = argparse.ArgumentParser()
parser.add_argument("name", help="Name of the new plugin")

args = parser.parse_args()

PLUGINS_DIRECTORY = "lisp/plugins"


def create_plugin(name: str):
    print(">>> CREATE NEW PLUGIN: {}".format(name))

    if not name.isidentifier():
        print("Invalid plugin name!", file=sys.stderr)
        sys.exit(-1)

    plugin_path = os.path.join(PLUGINS_DIRECTORY, name)
    class_name = module_to_class_name(name)

    os.makedirs(plugin_path)
    print(">>> DIRECTORY {} CREATED".format(plugin_path))

    print(">>> CREATE DEFAULT SETTINGS FILE")
    copyfile(
        os.path.join(PLUGINS_DIRECTORY, "default.json"),
        os.path.join(plugin_path, "default.json"),
    )

    print(">>> CREATE DEFAULT INIT FILE")
    with open(os.path.join(plugin_path, "__init__.py"), "w") as init_file:
        init_file.write(
            "# Auto-generated __init__.py for plugin\n"
            "from .{} import {}\n".format(name, class_name)
        )

    print(">>> CREATE DEFAULT MAIN PLUGIN FILE")
    with open(os.path.join(plugin_path, name + ".py"), "w") as main_plugin:
        main_plugin.write(
            "# Auto-generated plugin\n"
            "from lisp.core.plugin import Plugin\n\n\n"
            "class {0}(Plugin):\n"
            '    Name = "{0}"\n'
            '    Authors = ("Nobody", )\n'
            '    Description = "No Description"\n'.format(class_name)
        )

    print(">>> DONE")


try:
    create_plugin(args.name)
except OSError as e:
    print(str(e), file=sys.stderr)
