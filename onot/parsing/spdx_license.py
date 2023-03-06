#!/usr/bin/env python3

# SPDX-FileCopyrightText: Copyright 2022 SK TELECOM CO., LTD. <haksung@sk.com>
# SPDX-FileCopyrightText: Copyright (c) 2022 Kakao Corp. https://www.kakaocorp.com
#
# SPDX-License-Identifier: Apache-2.0

import requests
import logging

SPDX_LICENSE_URL_PREFIX = "https://spdx.org/licenses/"
SPDX_LICENSE_JSON_URL = "https://spdx.org/licenses/licenses.json"
SPDX_LICENSE_EXCEPTION_JSON_URL = "https://spdx.org/licenses/exceptions.json"

logger = logging.getLogger("root")

class SPDX_License():

    def __init__(self):
        logger.debug("SPDX_License")
        self.spdx_license_list = []
        self.spdx_license_exception_list = []

    def get_spdx_license_list(self):
        r = requests.get(SPDX_LICENSE_JSON_URL)
        self.spdx_license_list = r.json()

    def get_spdx_license_exception_list(self):
        r = requests.get(SPDX_LICENSE_EXCEPTION_JSON_URL)
        self.spdx_license_exception_list = r.json()
    
    def get_spdx_license_detailsUrl(self, license_id):
        logger.debug("licenseid - " + license_id)
        if not self.spdx_license_list: # list is empty
            self.get_spdx_license_list()
        if not self.spdx_license_exception_list: # list is empty
            self.get_spdx_license_exception_list()

        for spdx_license in self.spdx_license_list['licenses']:
            if spdx_license['licenseId'] == license_id:
                return spdx_license['detailsUrl']
        for spdx_license_exception in self.spdx_license_exception_list['exceptions']:
            if spdx_license_exception['licenseExceptionId'] == license_id:
                return SPDX_LICENSE_URL_PREFIX + str(spdx_license_exception['reference']).replace("./", "")

        return None
    
    def get_spdx_license_details(self, details_url):
        r = requests.get(details_url)
        detalis_license = r.json()

        # convert to license form if detalis_license is license exception
        if "licenseId" not in detalis_license:
            detalis_license['licenseId'] = detalis_license['licenseExceptionId']
        if 'licenseText' not in detalis_license:
            detalis_license['licenseText'] = detalis_license['licenseExceptionText']
        if 'licenseTextHtml' not in detalis_license:
            detalis_license['licenseTextHtml'] = detalis_license['exceptionTextHtml']

        return detalis_license