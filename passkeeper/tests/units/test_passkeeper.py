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
import passkeeper
from passkeeper import Passkeeper
from mock import patch, call, mock_open, MagicMock, Mock

class PasskeeperTestCase(test_base.TestCase):

    @patch('passkeeper.Git')
    def setUp(self, mock_git):
        super(PasskeeperTestCase, self).setUp()
        self.mock_git = mock_git
        self.pk = Passkeeper('foo')

    def tearDown(self):
        super(PasskeeperTestCase, self).tearDown()
        del self.pk
        del self.mock_git

    def test_constructor(self):
        self.mock_git.assert_called_once_with('foo')
        self.assertEquals(self.pk.directory, 'foo')
        self.assertEquals(self.pk.encrypted_dir, 'encrypted')


    @patch('passkeeper.Passkeeper.cleanup_ini')
    @patch('passkeeper.Passkeeper.encrypt')
    @patch('passkeeper.create_dir')
    def test_init_dir(self, mock_create_dir, mock_encrypt, mock_cleanup):
        self.mock_git.reset_mock()
        with patch('__builtin__.open', mock_open(), create=True) as file_mock:
            file_handle = file_mock()
            self.pk.init_dir(passphrase='secret')

        calls = [call().init(), call().add_gitignore(['*.ini', '/*.raw'])]
        self.mock_git.assert_has_calls(calls)

        calls = [call('foo'), call('foo/default.raw')]
        mock_create_dir.assert_has_calls(calls)

        file_mock.assert_any_call('foo/default.ini', 'w')
        file_mock.assert_any_call('foo/default.raw/ssh_id.rsa', 'w')

        self.assertEquals(True, file_handle.write.called)

        mock_encrypt.assert_called_once_with(passphrase='secret')
        mock_cleanup.assert_called_once_with()


    @patch('passkeeper.Passkeeper._remove_old_encrypted_files')
    @patch('passkeeper.run_cmd')
    @patch('passkeeper.os.listdir')
    @patch('passkeeper.os.path.isfile')
    def test_cleanup_ini(self, mock_isfile, mock_listdir, mock_cmd,
                               mock_remove_old_encrypted_files):
        # One ignored file and one valid file
        mock_listdir.return_value = ['ignored', 'bar.ini']
        mock_isfile.return_value = True
        self.pk.cleanup_ini()

        mock_cmd.assert_called_once_with('shred --remove foo/bar.ini')
        mock_remove_old_encrypted_files.assert_called_once_with(force_remove=False)

        # Test with bad filepath. Do nothing
        mock_cmd.reset_mock()
        mock_listdir.return_value = ['bar.ini']
        mock_isfile.return_value = False
        self.pk.cleanup_ini()

        self.assertEquals(mock_cmd.call_count, 0)


    @patch('passkeeper.raw_input')
    @patch('passkeeper.run_cmd')
    @patch('passkeeper.os.listdir')
    @patch('passkeeper.os.path.isfile')
    def test__remove_old_encrypted_files(self, mock_isfile, mock_listdir,
                               mock_cmd, mock_raw_input):
        # One file and 3 in encrypted so delete one.
        # Basicly the script will remove 2 file.
        # But we will cancel one of them
        #  * bar keep
        #  * foo delete canceled
        #  * bli deleted

        mock_raw_input.side_effect = ['n', 'y']
        # listdir is used by walk
        mock_listdir.return_value = [ 'bar.ini.passkeeper',
                                      'foo.ini.passkeeper',
                                      'dir/bli.ini.passkeeper']
        mock_isfile.side_effect = [ True, False, False ]
        self.pk._remove_old_encrypted_files(force_remove=False)

        mock_cmd.assert_called_once_with('shred foo/encrypted/dir/bli.ini.passkeeper')
        calls = [ call().force_remove(['encrypted/dir/bli.ini.passkeeper']),
                  call().commit('Remove file encrypted/dir/bli.ini.passkeeper')]
        self.mock_git.assert_has_calls(calls)

        # Same test with force remove.
        # Never ask confirmation, just delete both files
        mock_cmd.reset_mock()
        mock_raw_input.reset_mock()
        mock_isfile.side_effect = [ True, False, False ]

        self.pk._remove_old_encrypted_files(force_remove=True)

        self.assertEquals(2, mock_cmd.call_count)
        self.assertEquals(0, mock_raw_input.call_count)


    @patch('passkeeper.decrypt')
    @patch('passkeeper.os.listdir')
    @patch('passkeeper.os.path.isfile')
    def test_decrypt(self, mock_isfile, mock_listdir, mock_decrypt):
        # One ignored file, one valid file adn one file in raw dir.
        # Used in walk dir
        mock_listdir.return_value = ['ignored', 'bar.ini.passkeeper', 'foo.raw/bli.passkeeper']
        mock_isfile.return_value = True
        self.pk.decrypt(passphrase='secret')

        mock_decrypt.assert_any_call(output='foo/bar.ini', passphrase='secret',
                                     source='foo/encrypted/bar.ini.passkeeper')
        mock_decrypt.assert_any_call(output='foo/foo.raw/bli', passphrase='secret',
                                     source='foo/encrypted/foo.raw/bli.passkeeper')

        # Test with bad filepath. Do nothing
        mock_decrypt.reset_mock()
        mock_listdir.return_value = ['bad_fake_file']
        mock_isfile.return_value = False
        self.pk.decrypt(passphrase='secret')

        self.assertEquals(mock_decrypt.call_count, 0)


    @patch('passkeeper.create_dir')
    @patch('passkeeper.encrypt')
    @patch('passkeeper.os.listdir')
    @patch('passkeeper.os.path.isfile')
    def test_encrypt(self, mock_isfile, mock_listdir, mock_encrypt, mock_create_dir):
        # Test with bad filepath. Don't encrypt this file
        mock_encrypt.reset_mock()
        self.mock_git.reset_mock()
        mock_listdir.return_value = ['fake_bar_file.ini']
        mock_isfile.return_value = False

        self.assertTrue(self.pk.encrypt(passphrase='secret'))
        self.assertEquals(mock_encrypt.call_count, 0)

        # One ignored file and one valid file
        # And one file in raw subdir
        mock_encrypt.reset_mock()
        self.mock_git.reset_mock()
        mock_create_dir.reset_mock()
        # First for listdir, second for walk
        mock_listdir.side_effect = [['ignored', 'bar.ini', 'foo.raw'], ['bli']]
        mock_isfile.return_value = True

        self.assertTrue(self.pk.encrypt(passphrase='secret', commit_message='my message'))

        calls = [call('foo/encrypted'), call('foo/encrypted/foo.raw')]
        mock_create_dir.assert_has_calls(calls)

        mock_encrypt.assert_any_call(passphrase='secret',
                                     source='foo/bar.ini',
                                     output='foo/encrypted/bar.ini.passkeeper')
        mock_encrypt.assert_any_call(passphrase='secret',
                                     source='foo/foo.raw/bli',
                                     output='foo/encrypted/foo.raw/bli.passkeeper')
        calls = [call().add(['encrypted/bar.ini.passkeeper']),
                 call().add(['encrypted/foo.raw/bli.passkeeper']),
                 call().commit('my message')]
        self.mock_git.assert_has_calls(calls)


    @patch('passkeeper.ConfigParser.RawConfigParser')
    @patch('passkeeper.os.listdir')
    @patch('passkeeper.os.path.isfile')
    def test_search(self, mock_isfile, mock_listdir, mock_rawconfig):
        # One ignored file and one valid file
        # In this file we have 4 sections :
        # - one matching in section name
        # - one matching not matching at all
        # - one matching with value content
        mock_config = MagicMock()
        mock_config.sections.return_value = ['unmatched', 'WanTed', 'value']
        vals = {('unmatched',): [('foo', 'bar')],
                ('WanTed',): [('foo', 'bar')],
                ('value',): [('found', '.wanted.')]}
        def side_effect(*args):
            return vals[args]
        mock_config.items = MagicMock(side_effect=side_effect)
        mock_rawconfig.return_value = mock_config
        mock_listdir.return_value = ['ignored', 'bar.ini']
        mock_isfile.return_value = True
        config, matching_sections = self.pk.search(pattern='WANTED')

        mock_config.read.assert_called_once_with('foo/bar.ini')
        self.assertEquals(['WanTed', 'value'], matching_sections)

        # Test with bad filepath.
        mock_config = Mock()
        mock_config.sections.return_value = []
        mock_rawconfig.return_value = mock_config
        mock_listdir.return_value = ['bar.ini']
        mock_isfile.return_value = False
        config, matching_sections = self.pk.search(pattern='WANTED')

        self.assertEquals(mock_config.read.call_count, 0)
        self.assertEquals([], matching_sections)


    @patch('passkeeper.shred_dir')
    def test_flush_history(self, mock_shred):

        self.pk.flush_history()

        mock_shred.assert_called_once_with('foo/.git')
        calls = [ call().init(),
                  call().add(['encrypted', '.gitignore']),
                  call().commit('Clean git History')]

        self.mock_git.assert_has_calls(calls)
