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
from passkeeper.tools import *
from passkeeper.git import *
from passkeeper.crypt import *
from os.path import isfile, isdir
import shutil


class CoreTestCase(test_base.TestCase):

    def setUp(self):
        super(CoreTestCase, self).setUp()
        # Clean the directory if exist
        if isdir('.tox/foo'):
            shutil.rmtree('.tox/foo')

    def tearDown(self):
        super(CoreTestCase, self).tearDown()

    def test_core(self):

        #
        # init
        #
        pk = passkeeper.Passkeeper(directory='.tox/foo')

        # check we have nothing
        self.assertFalse(isdir('.tox/foo'))

        # Init directory
        pk.init_dir(passphrase='secret')

        # Check initialised
        self.assertTrue(isdir('.tox/foo'))
        self.assertTrue(isdir('.tox/foo/.git'))
        self.assertTrue(isfile('.tox/foo/.gitignore'))
        self.assertFalse(isdir('.tox/foo/default.raw'))
        self.assertFalse(isfile('.tox/foo/default.ini'))
        self.assertFalse(isfile('.tox/foo/default.raw/ssh_id.rsa'))

        self.assertTrue(isdir('.tox/foo/encrypted'))
        self.assertTrue(isdir('.tox/foo/encrypted/default.raw'))
        self.assertTrue(isfile('.tox/foo/encrypted/default.ini.passkeeper'))
        self.assertTrue(isfile('.tox/foo/encrypted/default.raw/ssh_id.rsa.passkeeper'))
        self.assertStringInFile(filename='.tox/foo/encrypted/default.ini.passkeeper',
                                pattern='BEGIN PGP MESSAGE')

        # At this state we should have 2 log line.
        # 1 add gitignore file
        # 2 first encrypt commit
        git_logs = self._get_file_lines(filename='.tox/foo/.git/logs/HEAD')
        self.assertEquals(2, len(git_logs))

        #
        # Decrypt files
        #
        pk.decrypt(passphrase='secret')

        self.assertTrue(isfile('.tox/foo/default.ini'))
        self.assertStringInFile(filename='.tox/foo/default.ini',
                                pattern='foo is good website')
        self.assertTrue(isfile('.tox/foo/default.raw/ssh_id.rsa'))

        # Add input in file
        sample_file = ("""[bar]
name = bar access
type = web
url = http://bar.com
password = bar
login = bar
comments = bar is good website
""")
        with open('.tox/foo/default.ini', 'a') as f:
            f.write(sample_file)

        # At this state we should stay 2
        git_logs = self._get_file_lines(filename='.tox/foo/.git/logs/HEAD')
        self.assertEquals(2, len(git_logs))

        #
        # Encrypt files
        #
        pk.encrypt(passphrase='secret', commit_message='Add bar entry')

        # all file should say
        self.assertTrue(isfile('.tox/foo/default.ini'))
        self.assertTrue(isfile('.tox/foo/default.raw/ssh_id.rsa'))

        # At this state we should have our new commit (last line)
        git_logs = self._get_file_lines(filename='.tox/foo/.git/logs/HEAD')
        self.assertTrue('Add bar entry' in git_logs[-1])
        self.assertStringInFile(filename='.tox/foo/encrypted/default.ini.passkeeper',
                                pattern='BEGIN PGP MESSAGE')

        # Call cleanup ini files
        pk.cleanup_ini()

        # Ini file should not stay
        self.assertFalse(isfile('.tox/foo/default.ini'))
        self.assertFalse(isfile('.tox/foo/default.raw/ssh_id.rsa'))
        self.assertFalse(isdir('.tox/foo/default.raw'))

        #
        # Decrypt file (last validation)
        #
        pk.decrypt(passphrase='secret')

        self.assertStringInFile(filename='.tox/foo/default.ini',
                                pattern='bar is good website')

    def test_add_file(self):

        # init
        pk = passkeeper.Passkeeper(directory='.tox/foo')
        # Init directory
        pk.init_dir(passphrase='secret')
        # Decrypt files
        pk.decrypt(passphrase='secret')

        # Add new bar.ini file
        sample_file = ("""[bar]
name = bar access
type = web
url = http://bar.com
password = bar
login = bar
comments = bar is good website
""")
        with open('.tox/foo/bar.ini', 'w') as f:
            f.write(sample_file)

        # Add raw dir and file in it
        create_dir('.tox/foo/bar.raw/')
        sample_file = ("""My private data""")
        with open('.tox/foo/bar.raw/private', 'w') as f:
            f.write(sample_file)

        # Encrypt files
        pk.encrypt(passphrase='secret')
        # Call cleanup ini files
        pk.cleanup_ini()
        self.assertFalse(isfile('.tox/foo/bar.ini'))
        self.assertFalse(isdir('.tox/foo/bar.raw'))
        self.assertTrue(isfile('.tox/foo/encrypted/default.ini.passkeeper'))
        self.assertTrue(isfile('.tox/foo/encrypted/bar.ini.passkeeper'))
        self.assertTrue(isfile('.tox/foo/encrypted/bar.raw/private.passkeeper'))
        self.assertStringInFile(filename='.tox/foo/encrypted/bar.ini.passkeeper',
                                pattern='BEGIN PGP MESSAGE')
        self.assertStringInFile(filename='.tox/foo/encrypted/bar.raw/private.passkeeper',
                                pattern='BEGIN PGP MESSAGE')

        # re Decrypt files
        pk.decrypt(passphrase='secret')
        self.assertTrue(isfile('.tox/foo/bar.ini'))
        self.assertStringInFile(filename='.tox/foo/bar.ini',
                                pattern='bar is good website')
        self.assertTrue(isfile('.tox/foo/bar.raw/private'))
        self.assertStringInFile(filename='.tox/foo/bar.raw/private',
                                pattern='My private data')



    # Test flush history
    def test_flush_history(self):
        # init
        pk = passkeeper.Passkeeper(directory='.tox/foo')
        # Init directory
        pk.init_dir(passphrase='secret')
        # Decrypt files
        pk.decrypt(passphrase='secret')

        # Add input in file
        sample_file = ("""[bar]
name = bar access
type = web
url = http://bar.com
password = bar
login = bar
comments = bar is good website
""")
        with open('.tox/foo/bar.ini', 'a') as f:
            f.write(sample_file)

        # Encrypt files
        pk.encrypt(passphrase='secret', commit_message='Add bar entry')
        # Call cleanup ini files
        pk.cleanup_ini()

        # Check number of commit
        git_logs = self._get_file_lines(filename='.tox/foo/.git/logs/HEAD')
        self.assertEquals(3, len(git_logs))
        self.assertStringInFile(filename='.tox/foo/.git/logs/HEAD',
                                pattern='Add bar entry')

        # flush
        pk.flush_history()

        # Check files are still there
        self.assertTrue(isfile('.tox/foo/encrypted/default.ini.passkeeper'))
        self.assertTrue(isfile('.tox/foo/encrypted/bar.ini.passkeeper'))

        # At this state we should have only one new commit (Clean history)
        git_logs = self._get_file_lines(filename='.tox/foo/.git/logs/HEAD')
        self.assertEquals(1, len(git_logs))
        self.assertStringInFile(filename='.tox/foo/.git/logs/HEAD',
                                pattern='Clean git History')

    def test_delete_file(self):
        """ Create a new file. Decrypt this file and delete it.
        The encrypted file should be delete at the cleanup function"""
        # Fake raw_input 
        passkeeper.raw_input = lambda x: 'y'

        # init
        pk = passkeeper.Passkeeper(directory='.tox/foo')
        # Init directory
        pk.init_dir(passphrase='secret')
        # Decrypt files
        pk.decrypt(passphrase='secret')

        # Add input in file
        sample_file = ("""[bar]
name = bar access
""")
        with open('.tox/foo/bar.ini', 'a') as f:
            f.write(sample_file)

        # Add raw dir and file in it
        create_dir('.tox/foo/bar.raw/')
        sample_file = ("""My private data""")
        with open('.tox/foo/bar.raw/private', 'w') as f:
            f.write(sample_file)

        # Encrypt files
        pk.encrypt(passphrase='secret', commit_message='Add bar entry')
        # Call cleanup ini files
        pk.cleanup_ini()

        # Decrypt file (last validation)
        pk.decrypt(passphrase='secret')
        os.remove('.tox/foo/bar.ini')
        shutil.rmtree('.tox/foo/bar.raw/')


        # Encrypt files
        pk.encrypt(passphrase='secret', commit_message='Will remove bar.ini and bar.raw/*')


        # Control state befor
        self.assertTrue(isfile('.tox/foo/encrypted/bar.ini.passkeeper'))
        self.assertTrue(isfile('.tox/foo/encrypted/bar.raw/private.passkeeper'))
        git_logs = self._get_file_lines(filename='.tox/foo/.git/logs/HEAD')
        self.assertTrue('Will remove bar.ini and bar.raw/*' in git_logs[-1])

        # Call cleanup. file bar.passkeeped should be remove
        pk.cleanup_ini()

        # Should have a commit for file deleted
        self.assertFalse(isfile('.tox/foo/encrypted/bar.ini.passkeeper'))
        self.assertTrue(isfile('.tox/foo/encrypted/default.ini.passkeeper'))
        self.assertFalse(isfile('.tox/foo/encrypted/bar.raw/private.passkeeper'))
        self.assertFalse(isdir('.tox/foo/encrypted/bar.raw'))
        git_logs = self._get_file_lines(filename='.tox/foo/.git/logs/HEAD')
        self.assertTrue('Remove file encrypted/bar.raw/private.passkeeper' in git_logs[-2])
        self.assertTrue('Remove file encrypted/bar.ini.passkeeper' in git_logs[-1])


# Search in a file
#        # Search in files
#        elif args.search:
#            config, matching = pk.search(args.search)
#            pk.print_sections(config=config,
#                              pattern=args.search,
#                              matching_sections=matching)

