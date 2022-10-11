#!/usr/bin/env python3

# SPDX-FileCopyrightText: Copyright 2022 SK TELECOM CO., LTD. <haksung@sk.com>
# SPDX-License-Identifier: Apache-2.0
import openpyxl
import pandas as pd
from onot.parsing import spdx_license

# sheets
SHEET_DOCUMENT_INFO = "Document Info"
SHEET_PACKAGE_INFO = "Package Info"
SHEET_EXTRACTED_LICENSE_INFO = "Extracted License Info"

# columns
COLUMN_DOCUMENT_NAME = "Document Name"
COLUMN_CREATOR = "Creator"
COLUMN_PACKAGE_NAME = "Package Name"
COLUMN_PACKAGE_VERSION = "Package Version"
COLUMN_PACKAGE_DOWNLOAD_LOCATION = "Package Download Location"
COLUMN_LICENSE_CONCLUDED = "License Concluded"
COLUMN_LICENSE_DECLARED = "License Declared"
COLUMN_PACKAGE_COPYRIGHT_TEXT = "Package Copyright Text"
COLUMN_IDENTIFIER = "Identifier"
COLUMN_EXTRACTED_TEXT = "Extracted Text"
COLUMN_LICENSE_NAME = "License Name"

class Parser():

    def __init__(self, file):
        print("debug:" + "excel Parser class")
        self.wb = openpyxl.load_workbook(file)
        self.doc = {}

    def validate_sheet(self, file):
        # validate file contents : all necessary information should be in the file.
        # sheet & columns
        # 1. Document Info sheet
        # - Document Name 
        # - Creator (Organization / Email)
        # 2. Package Info
        # - Package Name
        # - Package Version
        # - Package Download Location
        # - License Concluded
        # - Package Copyright Text
        ws_names = self.wb.sheetnames
        print("debug: " + str(ws_names))
        required_sheets = [
            SHEET_DOCUMENT_INFO,
            SHEET_PACKAGE_INFO,
            # SHEET_EXTRACTED_LICENSE_INFO,
        ]
        for sheet in required_sheets:
            if sheet not in ws_names:
                raise ValueError("required sheet is not existed: " + sheet)  

    def document_info(self):
        sheet = self.wb.get_sheet_by_name(SHEET_DOCUMENT_INFO)
        df = pd.DataFrame(sheet.values)
        df.columns = df.iloc[0, :]
        df = df.iloc[1:, :]
        
        # get document name
        document_name = df.loc[:, COLUMN_DOCUMENT_NAME].values.tolist()
        if document_name[0] is not None:
            self.doc["name"] = document_name[0]
        else:
            raise ValueError("required value is not existed: " + COLUMN_DOCUMENT_NAME) 
        
        # get organization & email 
        creator_info = df.loc[:, COLUMN_CREATOR].values.tolist()
        for creator in creator_info:
            if 'Organization' in creator:
                if '@' in creator:
                    organization_email = creator.replace('Organization: ', '').split('(')
                    organization = organization_email[0].strip()
                    email = organization_email[1].replace(')', '')
                    creation_info = {
                        "organization": organization,
                        "email": email, 
                    }
                    self.doc["creationInfo"] = creation_info
                else:
                    raise ValueError("email info is not existed.") 
        if "creationInfo" not in self.doc:
            raise ValueError("Organization info is not existed in the " + SHEET_DOCUMENT_INFO) 

    def package_info(self):
        sheet = self.wb.get_sheet_by_name(SHEET_PACKAGE_INFO)
        df = pd.DataFrame(sheet.values)
        df.columns = df.iloc[0, :]
        df = df.iloc[1:, :]
        
        # get package info
        # validate necessary columns are existed
        if COLUMN_PACKAGE_NAME not in df.columns:
            raise ValueError("required column is not existed: " + COLUMN_PACKAGE_NAME) 
        if COLUMN_PACKAGE_VERSION not in df.columns:
            raise ValueError("required column is not existed: " + COLUMN_PACKAGE_VERSION) 
        if COLUMN_LICENSE_CONCLUDED not in df.columns:
            raise ValueError("required column is not existed: " + COLUMN_LICENSE_CONCLUDED) 
        if COLUMN_LICENSE_DECLARED not in df.columns:
            raise ValueError("required column is not existed: " + COLUMN_LICENSE_DECLARED) 
        if COLUMN_PACKAGE_COPYRIGHT_TEXT not in df.columns:
            raise ValueError("required column is not existed: " + COLUMN_PACKAGE_COPYRIGHT_TEXT) 
        if COLUMN_PACKAGE_DOWNLOAD_LOCATION not in df.columns:
            raise ValueError("required column is not existed: " + COLUMN_PACKAGE_DOWNLOAD_LOCATION) 

        package_info_list = df.loc[:, 
            [
                COLUMN_PACKAGE_NAME, 
                COLUMN_PACKAGE_VERSION,
                COLUMN_LICENSE_CONCLUDED,
                COLUMN_LICENSE_DECLARED,
                COLUMN_PACKAGE_COPYRIGHT_TEXT,
                COLUMN_PACKAGE_DOWNLOAD_LOCATION,
                ]].values.tolist()
        self.packages = []
        for package_info in package_info_list:
            # None check
            for index, value in enumerate(package_info):
                if value is None:
                    package_info[index] = ''
            package = {
                "name": package_info[0],
                "versionInfo": str(package_info[1]),
                "licenseConcluded": package_info[2],
                "licenseDeclared": package_info[3],
                "copyrightText": package_info[4],
                "downloadLocation": package_info[5],
            }
            self.packages.append(package)
        self.doc["packages"] = self.packages

    def extracted_license_info(self):
        sheet = self.wb.get_sheet_by_name(SHEET_EXTRACTED_LICENSE_INFO)
        df = pd.DataFrame(sheet.values)
        df.columns = df.iloc[0, :]
        df = df.iloc[1:, :]
        
        # get package info
        # validate necessary columns are existed
        if COLUMN_IDENTIFIER not in df.columns:
            raise ValueError("required column is not existed: " + COLUMN_IDENTIFIER) 
        if COLUMN_EXTRACTED_TEXT not in df.columns:
            raise ValueError("required column is not existed: " + COLUMN_EXTRACTED_TEXT) 
        if COLUMN_LICENSE_NAME not in df.columns:
            raise ValueError("required column is not existed: " + COLUMN_LICENSE_NAME) 
        
        extracted_license_list = df.loc[:, 
            [
                COLUMN_IDENTIFIER, 
                COLUMN_EXTRACTED_TEXT,
                COLUMN_LICENSE_NAME,
                ]].values.tolist()
        self.extracted_licenses = []
        for extracted_license_info in extracted_license_list:
            extracted_license = {
                "identifier": extracted_license_info[0],
                "extractedText": extracted_license_info[1],
                "licenseName": extracted_license_info[2],
            }
            self.extracted_licenses.append(extracted_license)
        self.doc["extracted_license"] = self.extracted_licenses

    def license_info(self):
        self.licenses = []
        license = {}
        packages = []
        sl = spdx_license.SPDX_License()
        
        # get necessary license info
        for package in self.packages:
            package_name = package["name"]
            package_version = str(package["versionInfo"])
            license_name = package["licenseConcluded"]
            if license_name is None:
                license_name = package["licenseDeclared"]
            
            # check whether the licenseId is existed in the spdx license list
            details_url = sl.get_spdx_license_detailsUrl(license_name)
            print("debug: " + str(details_url))
            if details_url is not None:
                # if so, get the license text from spdx repo : "https://spdx.org/licenses/[LICENSE_ID].json"
                detalis_license = sl.get_spdx_license_details(details_url)
            else:
                # if not, get the license text from External Refs sheet
                if "extracted_license" not in self.doc:
                    self.extracted_license_info()
                
                # check the license is in the Extracted License Info sheet
                existed_in_extracted_license = False
                for index, extracted_license in enumerate(self.doc['extracted_license']):
                    if extracted_license['identifier'] == license_name:
                        detalis_license = {
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
            license_appended = False
            for index, license in enumerate(self.licenses):
                if license["licenseId"] == detalis_license['licenseId']:
                    # then, update data just to add package info
                    target_license = license
                    target_package = license['packages']
                    target_package.append((package_name, package_version))
                    target_license['packages'] = target_package
                    self.licenses[index] = target_license
                    license_appended = True
                    break
            if not license_appended:
                packages = []
                packages.append((package_name, package_version))
                license = {
                    "name": detalis_license['name'],
                    "licenseId": detalis_license['licenseId'],
                    "packages" : packages,
                    "licenseText": detalis_license['licenseText'],
                    "licenseTextHtml": detalis_license['licenseTextHtml']
                }
                self.licenses.append(license)
            
        self.doc["licenses"] = self.licenses

    def load_doc(self, file):

        # Document info
        self.document_info()

        # Package info
        self.package_info()

        # License info
        self.license_info()

        return self.doc

    def parse(self, file):
        print("debug: " + "parse")

        self.validate_sheet(file)
        doc = self.load_doc(file)
        return doc
            
