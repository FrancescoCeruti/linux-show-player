# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2015 Francesco Ceruti <ceppofrancy@gmail.com>
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

from configparser import ConfigParser
import os
from shutil import copyfile

from lisp.utils import util


DEFAULT_CFG_PATH = util.file_path(__file__, '../default.cfg')
CFG_DIR = os.path.expanduser("~") + '/.linux_show_player'
CFG_PATH = CFG_DIR + '/config.cfg'


def check_user_conf():
    update = True

    if not os.path.exists(CFG_DIR):
        os.makedirs(CFG_DIR)
    elif os.path.exists(CFG_PATH):
        default = ConfigParser()
        default.read(DEFAULT_CFG_PATH)

        current = ConfigParser()
        current.read(CFG_PATH)

        current_version = current['Version'].get('Number', None)
        update = current_version != default['Version']['Number']

        if update:
            copyfile(CFG_PATH, CFG_PATH + '.old')
            print('Old configuration file backup -> ' + CFG_PATH + '.old')

    if update:
        copyfile(DEFAULT_CFG_PATH, CFG_PATH)
        print('Create configuration file -> ' + CFG_PATH)
    else:
        print('Configuration is up to date')

# Check if the current user configuration is up-to-date
check_user_conf()

# Read the user configuration
config = ConfigParser()
config.read(CFG_PATH)


def config_to_dict():
    conf_dict = {}

    for section in config.keys():
        conf_dict[section] = {}
        for option in config[section].keys():
            conf_dict[section][option] = config[section][option]

    return conf_dict


def update_config_from_dict(conf):
    for section in conf.keys():
        for option in conf[section].keys():
            config[section][option] = conf[section][option]

    write_config()


def write_config():
    with open(CFG_PATH, 'w') as f:
        config.write(f)
