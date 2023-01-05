# !/usr/bin/env python3

# SPDX-FileCopyrightText: Copyright 2022 SK TELECOM CO., LTD. <haksung@sk.com>
# SPDX-FileCopyrightText: Copyright (c) 2022 Kakao Corp. https://www.kakaocorp.com
#
# SPDX-License-Identifier: Apache-2.0
import unittest
from onot.parsing import spdx_license

class TestGetSPDXLicenseCase(unittest.TestCase):
    # license and license exception from spdx-spec/v2.3
    # https://spdx.github.io/spdx-spec/v2.3/SPDX-license-list/#a1-licenses-with-short-identifiers
    # https://spdx.github.io/spdx-spec/v2.3/SPDX-license-list/#a2-exceptions-list
    licenses = ['Apache-2.0', 'BSD-3-Clause', 'EPL-2.0', 'LGPL-2.1-only', 'MPL-2.0',
                'Autoconf-exception-2.0', 'Bison-exception-2.2', 'GCC-exception-2.0']

    def setUp(self):
        self.instance = spdx_license.SPDX_License()

    def tearDown(self):
        # self.instance.dispose()
        del self.instance

    def test_result(self):
        for license in self.licenses:
            with self.subTest(license=license):
                details_url = self.instance.get_spdx_license_detailsUrl(license)
                license_details = self.instance.get_spdx_license_details(details_url)
                self.assertTrue(license_details['licenseId'] is not None or license_details['licenseExceptionId'] is not None)

