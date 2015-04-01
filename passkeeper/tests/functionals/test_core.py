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

        # init
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

    
#        # Decrypt files
#        elif args.decrypt:
#            pk.decrypt()
#        # Search in files
#        elif args.search:
#            config, matching = pk.search(args.search)
#            pk.print_sections(config=config,
#                              pattern=args.search,
#                              matching_sections=matching)
#        # Encrypt files
#        elif args.encrypt:
#            if args.commit_message:
#                status = pk.encrypt(commit_message=args.commit_message)
#            else:
#                status = pk.encrypt()
#            if status:
#                pk.cleanup_ini()
#
