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

import base as test_base
from passkeeper.git import Git
from mock import patch, call, mock_open

class GitTestCase(test_base.TestCase):

    def setUp(self):
        super(GitTestCase, self).setUp()
        self.git = Git('foo')

    def tearDown(self):
        super(GitTestCase, self).tearDown()
        del self.git

    def test_constructor(self):
        self.assertEquals(self.git.directory, 'foo')

    @patch('passkeeper.git.run_cmd')
    def test__run_git_cmd(self, mock_cmd):
        self.git._run_git_cmd('bar')

        # Will call bar command in foo directory
        self.assertEquals(mock_cmd.call_args,
                          call('git --work-tree=foo  --git-dir=foo/.git bar'))

    @patch('passkeeper.git.Git._run_git_cmd')
    def test_init(self, mock_git_cmd):
        self.git.init()

        calls = [call('init'), call('config user.name passkeeper')]
        mock_git_cmd.assert_has_calls(calls)

    @patch('passkeeper.git.Git._run_git_cmd')
    def test_add(self, mock_git_cmd):
        self.git.add(files = ['f1', 'f2'])

        calls = [call('add f1'), call('add f2')]
        mock_git_cmd.assert_has_calls(calls)

    @patch('passkeeper.git.Git._run_git_cmd')
    def test_soft_remove(self, mock_git_cmd):
        self.git.soft_remove(files = ['f1', 'f2'])

        calls = [call('rm --cached f1'), call('rm --cached f2')]
        mock_git_cmd.assert_has_calls(calls)

    @patch('passkeeper.git.Git._run_git_cmd')
    def test_force_remove(self, mock_git_cmd):
        self.git.force_remove(files = ['f1', 'f2'])

        calls = [call('rm --force f1'), call('rm --force f2')]
        mock_git_cmd.assert_has_calls(calls)

    @patch('passkeeper.git.Git._run_git_cmd')
    def test_remove(self, mock_git_cmd):
        self.git.remove(files = ['f1', 'f2'])

        calls = [call('rm f1'), call('rm f2')]
        mock_git_cmd.assert_has_calls(calls)

    @patch('passkeeper.git.Git._run_git_cmd')
    def test_commit(self, mock_git_cmd):
        self.git.commit(message = 'foo')

        calls = [call('commit -m "foo" || true')]
        mock_git_cmd.assert_has_calls(calls)

    @patch('passkeeper.git.Git.add')
    @patch('passkeeper.git.Git.commit')
    def test_add_gitignore(self, mock_commit, mock_add):
        with patch('__builtin__.open', mock_open(), create=True) as file_mock:
            handle = file_mock()
            self.git.add_gitignore(lines = ['foo', 'bar'])

            file_mock.assert_called_with('foo/.gitignore', 'w')
            handle.write.assert_called_once_with('foo\nbar')
        mock_add.assert_called_once_with(['.gitignore'])
        mock_commit.assert_called_once_with('Update .gitignore file')
