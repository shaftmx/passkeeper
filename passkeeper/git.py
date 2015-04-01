#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

    def add(self, files):
        for file in files:
            self._run_git_cmd('add %s' % file)

    def commit(self, message):
        self._run_git_cmd('commit -m "%s" || true' % message)

    def add_gitignore(self, lines):
        LOG.debug('Write .gitignore')
        gitignore_path = os_join(self.directory, '.gitignore')
        with open(gitignore_path, 'w') as f:
            f.write('\n'.join(lines))
        self.add(['.gitignore'])
        self.commit('Update .gitignore file')
