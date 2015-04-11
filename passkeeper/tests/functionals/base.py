# -*- coding: utf-8 -*-

import unittest2 as unittest

import mox
import stubout

class TestCase(unittest.TestCase):
    def setUp(self):
        super(TestCase, self).setUp()
        self.mox = mox.Mox()
        self.stubs = stubout.StubOutForTesting()

    def tearDown(self):
        self.mox.UnsetStubs()
        self.stubs.UnsetAll()
        self.stubs.SmartUnsetAll()
        self.mox.VerifyAll()
        super(TestCase, self).tearDown()

    def _string_in_file(self, filename, pattern):
        try:
            with open(filename, 'r') as f:
                content = f.read()
            if pattern in content:
                return True
            else:
                return False
        except:
            return False

    def assertStringInFile(self, filename, pattern):
        self.assertTrue(self._string_in_file(filename=filename,
                                             pattern=pattern))

    def _get_file_lines(self, filename):
        with open(filename, 'r') as f:
            _lines = f.readlines()
        return _lines

