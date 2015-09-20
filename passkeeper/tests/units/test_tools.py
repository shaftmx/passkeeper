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
from passkeeper.tools import *
from mock import patch, call, mock_open

class ToolsTestCase(test_base.TestCase):

    def setUp(self):
        super(ToolsTestCase, self).setUp()

    def tearDown(self):
        super(ToolsTestCase, self).tearDown()

    @patch('passkeeper.os.makedirs')
    @patch('passkeeper.os.path.isdir')
    def test_create_dir(self, mock_isdir, mock_makedirs):
        # Dry run do nothing
        create_dir(path='unittest', dry_run=True)
        self.assertEquals(mock_makedirs.call_count, 0)

        # Should create dir
        mock_makedirs.reset_mock()
        mock_isdir.return_value = False
        create_dir(path='unittest', dry_run=False)
        mock_makedirs.assert_called_once_with('unittest')

        # Dir already exist don't create it
        mock_makedirs.reset_mock()
        mock_isdir.return_value = True
        create_dir(path='unittest', dry_run=False)
        self.assertEquals(mock_makedirs.call_count, 0)

    @patch('passkeeper.subprocess.call')
    def test_run_cmd(self, mock_call):
        # Dry run do nothing
        run_cmd(cmd='foo', dry_run=True)
        self.assertEquals(mock_call.call_count, 0)

        # Valid command do it
        mock_call.reset_mock()
        mock_call.return_value = 0
        run_cmd(cmd='foo', dry_run=False)
        mock_call.assert_called_once_with('foo', shell=True)

        # In error state command. Expect run command and raise exception
        mock_call.reset_mock()
        mock_call.return_value = 1
        with self.assertRaises(Exception):
            run_cmd(cmd='foo', dry_run=False)
        mock_call.assert_called_once_with('foo', shell=True)


    @patch('passkeeper.tools.run_cmd')
    @patch('passkeeper.os.rmdir')
    @patch('passkeeper.os.walk')
    def test_shred_dir(self, mock_walk, mock_rmdir, mock_cmd):

        mock_walk.return_value = [ ('foo/.git', ['subdir1'], ['bli']), ('foo/.git/subdir1', [], ['bar'])]

        shred_dir('foo/.git')

        calls = [call('shred -f --remove foo/.git/bli'), call('shred -f --remove foo/.git/subdir1/bar')]
        mock_cmd.assert_has_calls(calls)

        calls = [call('foo/.git/subdir1'), call('foo/.git')]
        mock_rmdir.assert_has_calls(calls)
