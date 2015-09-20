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

import logging
from os.path import join as os_join
from passkeeper.tools import *

LOG = logging.getLogger(__name__)

class Git(object):

    def __init__(self, directory):
        self.directory = directory

    def _run_git_cmd(self, command):
        work_tree = self.directory
        git_dir = os_join(self.directory, '.git')
        git_cmd = 'git --work-tree=%s  --git-dir=%s %s' % (work_tree,
                                                           git_dir, command)
        LOG.debug('Launch : %s' % git_cmd)
        run_cmd(git_cmd)

    def init(self):
        self._run_git_cmd('init')
        self._run_git_cmd('config user.name passkeeper')
        self._run_git_cmd('config user.email you@example.com')

    def add(self, files):
        for file in files:
            self._run_git_cmd('add %s' % file)

    def soft_remove(self, files):
        for file in files:
            self._run_git_cmd('rm --cached %s' % file)

    def force_remove(self, files):
        for file in files:
            self._run_git_cmd('rm --force %s' % file)

    def remove(self, files):
        for file in files:
            self._run_git_cmd('rm %s' % file)

    def commit(self, message):
        self._run_git_cmd('commit -m "%s" || true' % message)

    def add_gitignore(self, lines):
        LOG.debug('Write .gitignore')
        gitignore_path = os_join(self.directory, '.gitignore')
        with open(gitignore_path, 'w') as f:
            f.write('\n'.join(lines))
        self.add(['.gitignore'])
        self.commit('Update .gitignore file')
