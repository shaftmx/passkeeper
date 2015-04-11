#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base as test_base


import passkeeper
from passkeeper.tools import *
from passkeeper.git import *
from passkeeper.crypt import *
import mock
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

        # Fake getpass
        passkeeper.getpass = mock.MagicMock()
        passkeeper.getpass.return_value = "foo"

        #
        # init
        #
        pk = passkeeper.Passkeeper(directory='.tox/foo')

        # check we have nothing
        self.assertFalse(isdir('.tox/foo'))

        # Init directory
        pk.init_dir()

        # Check initialised
        self.assertTrue(isdir('.tox/foo'))
        self.assertTrue(isdir('.tox/foo/.git'))
        self.assertTrue(isfile('.tox/foo/.gitignore'))
        self.assertFalse(isfile('.tox/foo/default.ini'))

        self.assertTrue(isdir('.tox/foo/encrypted'))
        self.assertTrue(isfile('.tox/foo/encrypted/default.ini.passkeeper'))
        self.assertTrue(self._string_in_file(filename = '.tox/foo/encrypted/default.ini.passkeeper',
                                        pattern = 'BEGIN PGP MESSAGE'))

        # At this state we should have 2 log line.
        # 1 add gitignore file
        # 2 first encrypt commit
        git_logs = self._get_file_lines(filename='.tox/foo/.git/logs/HEAD')
        self.assertEquals(2, len(git_logs))

        #
        # Decrypt files
        #
        pk.decrypt()

        self.assertTrue(isfile('.tox/foo/default.ini'))
        self.assertTrue(self._string_in_file(filename = '.tox/foo/default.ini',
                                        pattern = 'foo is good website'))

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
        pk.encrypt(commit_message='Add bar entry')

        # Ini file should stay
        self.assertTrue(isfile('.tox/foo/default.ini'))

        # At this state we should have our new commit (last line)
        git_logs = self._get_file_lines(filename='.tox/foo/.git/logs/HEAD')
        self.assertTrue( 'Add bar entry' in git_logs[-1] )
        self.assertTrue(self._string_in_file(filename = '.tox/foo/encrypted/default.ini.passkeeper',
                                        pattern = 'BEGIN PGP MESSAGE'))

        # Call cleanup ini files
        pk.cleanup_ini()

        # Ini file should stay
        self.assertFalse(isfile('.tox/foo/default.ini'))

        #
        # Decrypt file (last validation)
        #
        pk.decrypt()

        self.assertTrue(self._string_in_file(filename = '.tox/foo/default.ini',
                                        pattern = 'bar is good website'))

    def test_add_file(self):

        # Fake getpass
        passkeeper.getpass = mock.MagicMock()
        passkeeper.getpass.return_value = "foo"

        # init
        pk = passkeeper.Passkeeper(directory='.tox/foo')
        # Init directory
        pk.init_dir()
        # Decrypt files
        pk.decrypt()

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

        # Encrypt files
        pk.encrypt()
        # Call cleanup ini files
        pk.cleanup_ini()
        self.assertFalse(isfile('.tox/foo/bar.ini'))
        self.assertTrue(isfile('.tox/foo/encrypted/default.ini.passkeeper'))
        self.assertTrue(isfile('.tox/foo/encrypted/bar.ini.passkeeper'))
        self.assertTrue(self._string_in_file(filename = '.tox/foo/encrypted/bar.ini.passkeeper',
                                        pattern = 'BEGIN PGP MESSAGE'))

        # re Decrypt files
        pk.decrypt()
        self.assertTrue(isfile('.tox/foo/bar.ini'))
        self.assertTrue(self._string_in_file(filename = '.tox/foo/bar.ini',
                                        pattern = 'bar is good website'))



    # Test flush history
    def test_flush_history(self):
        # Fake getpass
        passkeeper.getpass = mock.MagicMock()
        passkeeper.getpass.return_value = "foo"

        # init
        pk = passkeeper.Passkeeper(directory='.tox/foo')
        # Init directory
        pk.init_dir()
        # Decrypt files
        pk.decrypt()

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
        pk.encrypt(commit_message='Add bar entry')
        # Call cleanup ini files
        pk.cleanup_ini()

        # Check number of commit
        git_logs = self._get_file_lines(filename='.tox/foo/.git/logs/HEAD')
        self.assertEquals(3, len(git_logs))
        self.assertTrue(self._string_in_file(filename = '.tox/foo/.git/logs/HEAD',
                                        pattern = 'Add bar entry'))

        # flush
        pk.flush_history()

        # Check files are still there
        self.assertTrue(isfile('.tox/foo/encrypted/default.ini.passkeeper'))
        self.assertTrue(isfile('.tox/foo/encrypted/bar.ini.passkeeper'))

        # At this state we should have only one new commit (Clean history)
        git_logs = self._get_file_lines(filename='.tox/foo/.git/logs/HEAD')
        self.assertEquals(1, len(git_logs))
        self.assertTrue(self._string_in_file(filename = '.tox/foo/.git/logs/HEAD',
                                        pattern = 'Clean git History'))

