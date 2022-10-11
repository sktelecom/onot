#!/usr/bin/env python3

# SPDX-FileCopyrightText: Copyright 2022 SK TELECOM CO., LTD. <haksung@sk.com>
# SPDX-License-Identifier: Apache-2.0
import requests

SPDX_LICENSE_JSON_URL = "https://spdx.org/licenses/licenses.json"

class SPDX_License():

    def __init__(self):
        print("debug:" + "SPDX_License")
        self.spdx_license_list = []
    
    def get_spdx_license_list(self):
        r = requests.get(SPDX_LICENSE_JSON_URL)
        self.spdx_license_list = r.json()
    
    def get_spdx_license_detailsUrl(self, license_id):
        print("debug:" + "licenseid - " + license_id)
        if not self.spdx_license_list: # list is empty
            self.get_spdx_license_list()
        for spdx_license in self.spdx_license_list['licenses']:
            if spdx_license['licenseId'] == license_id:
                return spdx_license['detailsUrl']
        return None
    
    def get_spdx_license_details(self, details_url):
        r = requests.get(details_url)
        detalis_license = r.json()
        return detalis_license

    
