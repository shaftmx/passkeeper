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

