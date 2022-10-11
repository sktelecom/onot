#!/usr/bin/env python3

# SPDX-FileCopyrightText: Copyright 2022 SK TELECOM CO., LTD. <haksung@sk.com>
# SPDX-License-Identifier: Apache-2.0
import unittest
from onot.parsing import excel

SAMPLE_FILE = 'sample/SPDXRdfExample-v2.1.xlsx'

class TestClass(unittest.TestCase):
    def setUp(self):
        self.instance = excel.Parser(SAMPLE_FILE)
        
    def tearDown(self):
        # self.instance.dispose()
        del self.instance
        
    def test_result(self):
        result=self.instance.parse(SAMPLE_FILE)
        # self.assertEqual(result, True)
        
    # def test_raise_exception(self):
    #     self.assertRaises(Exception, lambda: self.instance.example_method2())