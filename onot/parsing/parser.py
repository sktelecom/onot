#!/usr/bin/env python3

# SPDX-FileCopyrightText: Copyright 2022 SK TELECOM CO., LTD. <haksung@sk.com>
# SPDX-FileCopyrightText: Copyright (c) 2022 Kakao Corp. https://www.kakaocorp.com
#
# SPDX-License-Identifier: Apache-2.0

import os.path
import re
from abc import abstractmethod, ABC
import logging
from onot.parsing import spdx_license

logger = logging.getLogger("root")

class AbstractParser(ABC):

    def __init__(self):
        self.doc = {
            "name": "",
            "creation_info": {},
            "packages": [],
            "extracted_license": []
        }

    @abstractmethod
    def validate_file(self):
        pass

    @abstractmethod
    def document_info(self):
        # set self.doc["name"], self.doc["creation_info"]
        pass

    @abstractmethod
    def package_info(self):
        # set self.doc["packages"]
        pass

    @abstractmethod
    def per_file_info(self):
        # set self.doc["packages"]
        pass

    @abstractmethod
    def extracted_license_info(self):
        # set self.doc["extracted_license"]
        pass

    def append_package(self, package_to_be_appended):
        # Check if there are duplicate packages already appended
        if any(package["name"] == package_to_be_appended["name"] and package["versionInfo"] == package_to_be_appended["versionInfo"] for package in self.doc["packages"]):
            return
        self.doc["packages"].append(package_to_be_appended)

    def extract_package_name_and_package_version(self, filename):
        def remove_meaningless_word(_filename):
            _filename = _filename.replace("-sources", "")
            _filename = _filename.replace("-RELEASE", "")
            _filename = _filename.replace("-SNAPSHOT", "")
            return _filename

        filename = os.path.splitext(os.path.basename(filename))[0]
        filename = remove_meaningless_word(filename)
        version = re.search(r"-\d", filename)

        if version:
            return filename[:version.start()], filename[version.start() + 1:]
        else:
            return filename, ""

    def remove_enclosed_parentheses(self, expression):
        # if the overall expression is enclosed in parentheses, remove the parentheses.
        if str(expression).startswith("(") and str(expression).endswith(")"):
            return expression[1:len(expression)-1]
        return expression

    def parse_license_expression(self, license_expression):
        license_names = re.split(r'OR|AND|WITH', str(license_expression))
        # remove (, ), blank
        return list(map(lambda license: license.replace("(", "").replace(")", "").strip(), license_names))

    def add_package_info_if_license_exist(self, license_name, package_name, package_version):
        # then, update data just to add package info
        for index, license in enumerate(self.licenses):
            if license["licenseId"] == license_name:
                # then, update data just to add package info
                target_license = license
                target_package = license['packages']
                target_package.append((package_name, package_version))
                target_license['packages'] = target_package
                self.licenses[index] = target_license
                return True
        return False

    def get_details_license(self, license_name):
        sl = spdx_license.SPDX_License()

        # check whether the licenseId is existed in the spdx license list
        details_url = sl.get_spdx_license_detailsUrl(license_name)
        logger.debug(str(details_url))
        if details_url is not None:
            # if so, get the license text from spdx repo : "https://spdx.org/licenses/[LICENSE_ID].json"
            details_license = sl.get_spdx_license_details(details_url)
        else:
            # check the license is in the Extracted License Info sheet
            existed_in_extracted_license = False
            for index, extracted_license in enumerate(self.doc['extracted_license']):
                if extracted_license['identifier'] == license_name:
                    details_license = {
                        'licenseId': extracted_license['identifier'],
                        'name': extracted_license['licenseName'],
                        'licenseText': extracted_license['extractedText'],
                        'licenseTextHtml': None
                    }
                    existed_in_extracted_license = True
                    break
            if existed_in_extracted_license is False:
                raise ValueError("This license is not in the spdx license list. then it should be in the Extracted License Info sheet: " + license_name)

                # Check if there are duplicate licenses already appended
        return details_license

    def append_details_license(self, detalis_license, package_name, package_version):
        packages = []
        packages.append((package_name, package_version))
        license = {
            "name": detalis_license['name'],
            "licenseId": detalis_license['licenseId'],
            "packages": packages,
            "licenseText": detalis_license['licenseText'],
            "licenseTextHtml": detalis_license['licenseTextHtml']
        }
        self.licenses.append(license)

    def license_info(self):
        self.licenses = []

        # get necessary license info
        for package in self.doc["packages"]:
            package_name = package["name"]
            package_version = str(package["versionInfo"])
            license_expression = package["licenseConcluded"]
            if license_expression is None:
                license_expression = package["licenseDeclared"]

            license_names = self.parse_license_expression(license_expression)
            for license_name in license_names:
                if self.add_package_info_if_license_exist(license_name, package_name, package_version) is False:
                    details_license = self.get_details_license(license_name)
                    self.append_details_license(details_license, package_name, package_version)

        self.doc["licenses"] = self.licenses


    def load_doc(self, file):

        # Document info
        self.document_info()

        # Package info
        self.package_info()

        # Per File Info
        self.per_file_info()

        # Extracted License Info
        self.extracted_license_info()

        # License info
        self.license_info()

        return self.doc

    def parse(self, file):
        self.validate_file(file)
        doc = self.load_doc(file)
        return doc