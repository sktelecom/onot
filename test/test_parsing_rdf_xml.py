#!/usr/bin/env python3

# SPDX-FileCopyrightText: Copyright 2022 SK TELECOM CO., LTD. <haksung@sk.com>
# SPDX-FileCopyrightText: Copyright (c) 2022 Kakao Corp. https://www.kakaocorp.com
#
# SPDX-License-Identifier: Apache-2.0

import unittest

from onot.parsing import rdf_xml

SAMPLE_FILE = 'sample/SPDXRdfExample-v2.3.rdf.xml'

class TestParsingRdfXmlClass(unittest.TestCase):
    def setUp(self):
        self.instance = rdf_xml.Parser(SAMPLE_FILE)

    def tearDown(self):
        # self.instance.dispose()
        del self.instance

    def test_result(self):
        result = self.instance.parse(SAMPLE_FILE)
