#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base as test_base

class CoreTestCase(test_base.TestCase):

    def setUp(self):
        super(CoreTestCase, self).setUp()

    def tearDown(self):
        super(CoreTestCase, self).tearDown()

    def test_hello_unit(self):
        foo = True
        self.assertTrue(foo)
