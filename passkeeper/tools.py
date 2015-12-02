#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Gaël Lambert (gaelL) <gael.lambert@netwiki.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import logging
import subprocess
from os.path import join as os_join

LOG = logging.getLogger(__name__)


def white(texte):
    return "\033[37m%s\033[0m" % texte


def grey(texte):
    return "\033[30m%s\033[0m" % texte


def grey_strong(texte):
    return "\033[1;30m%s\033[0m" % texte


def blue(texte):
    return "\033[34m%s\033[0m" % texte


def red(texte):
    return "\033[31m%s\033[0m" % texte


def green(texte):
    return "\033[32m%s\033[0m" % texte


def pink(texte):
    return "\033[35m%s\033[0m" % texte


def yellow(texte):
    return "\033[33m%s\033[0m" % texte


def cyan(texte):
    return "\033[36m%s\033[0m" % texte


def create_dir(path, dry_run=False):
    if dry_run:
        LOG.warning('Create directory : %s' % path)
    else:
        if not os.path.isdir(path):
            LOG.info('Create directory : %s' % path)
            os.makedirs(path)


def run_cmd(cmd, dry_run=False):
    if dry_run:
        LOG.warning('Exec command %s' % cmd)
    else:
        LOG.debug('Exec command %s' % cmd)
        output = subprocess.call(cmd, shell=True)
        if output != 0:
            LOG.critical('Command ERROR %s return code : %d' % (cmd, output))
            raise Exception('Unable to execute command')


def shred_dir(directory):
    """
    Shred all files in directory and remove this directory.

    Shred files on a directory to avoid a malicious read

    :param directory: Path of directory to shred
    :type directory: str

    :Example:

    >>> shred_dir('/opt/mypasskeeper/.git')
    Clean file master
    Clean file HEAD
    Clean file exclude

    .. seealso:: run_cmd()
    """
    # Remove directory content
    for root, dirs, files in os.walk(directory, topdown=False):
        for fname in files:
            filepath = os_join(root, fname)
            LOG.info('Clean file %s' % fname)
            run_cmd('shred -f --remove %s' % filepath)
        for dname in dirs:
            dpath = os_join(root, dname)
            os.rmdir('%s' % dpath)
    # Remove the directory
    os.rmdir(directory)
