#!/usr/bin/env python3

# SPDX-FileCopyrightText: Copyright 2022 SK TELECOM CO., LTD. <haksung@sk.com>
# SPDX-FileCopyrightText: Copyright (c) 2022 Kakao Corp. https://www.kakaocorp.com
#
# SPDX-License-Identifier: Apache-2.0

import openpyxl
import pandas as pd
import logging
from onot.parsing import parser

# sheets
SHEET_DOCUMENT_INFO = "Document Info"
SHEET_PACKAGE_INFO = "Package Info"
SHEET_EXTRACTED_LICENSE_INFO = "Extracted License Info"
SHEET_PER_FILE_INFO = "Per File Info"

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
COLUMN_FILE_NAME = "File Name"
COLUMN_LICENSE_INFO_IN_FILE = "License Info in File"
COLUMN_FILE_COPYRIGHT_TEXT = "File Copyright Text"
COLUMN_ARTIFACT_OF_HOMEPAGE = "Artifact of Homepage"

logger = logging.getLogger("root")

class Parser(parser.AbstractParser):

    def __init__(self, file):
        super().__init__()
        logger.debug("excel Parser class")
        self.wb = openpyxl.load_workbook(file)

    def validate_file(self, file):
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
        # 3. Per File Info
        # - File Name
        # - Artifact of Homepage
        # - License Concluded
        # - License Info in File
        # - File Copyright Text
        ws_names = self.wb.sheetnames
        logger.debug(str(ws_names))
        required_sheets = [
            SHEET_DOCUMENT_INFO,
            SHEET_PACKAGE_INFO,
            SHEET_PER_FILE_INFO
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
                "licenseConcluded": self.remove_enclosed_parentheses(package_info[2]),
                "licenseDeclared": self.remove_enclosed_parentheses(package_info[3]),
                "copyrightText": package_info[4],
                "downloadLocation": package_info[5].replace("\"", ""),
            }
            self.append_package(package)

    def per_file_info(self):
        sheet = self.wb.get_sheet_by_name(SHEET_PER_FILE_INFO)
        df = pd.DataFrame(sheet.values)
        df.columns = df.iloc[0, :]
        df = df.iloc[1:, :]

        if COLUMN_FILE_NAME not in df.columns:
            raise ValueError("required column is not existed: " + COLUMN_FILE_NAME)
        if COLUMN_LICENSE_CONCLUDED not in df.columns:
            raise ValueError("required column is not existed: " + COLUMN_LICENSE_CONCLUDED)
        if COLUMN_LICENSE_INFO_IN_FILE not in df.columns:
            raise ValueError("required column is not existed: " + COLUMN_LICENSE_INFO_IN_FILE)
        if COLUMN_FILE_COPYRIGHT_TEXT not in df.columns:
            raise ValueError("required column is not existed: " + COLUMN_FILE_COPYRIGHT_TEXT)
        if COLUMN_ARTIFACT_OF_HOMEPAGE not in df.columns:
            raise ValueError("required column is not existed: " + COLUMN_ARTIFACT_OF_HOMEPAGE)

        per_file_info_list = df.loc[:,
            [
                COLUMN_FILE_NAME,
                COLUMN_LICENSE_CONCLUDED,
                COLUMN_LICENSE_INFO_IN_FILE,
                COLUMN_FILE_COPYRIGHT_TEXT,
                COLUMN_ARTIFACT_OF_HOMEPAGE
            ]].values.tolist()
        for per_file_info in per_file_info_list:
            for index, value in enumerate(per_file_info):
                if value is None:
                    per_file_info[index] = ''

            package_name, package_version = self.extract_package_name_and_package_version(per_file_info[0])
            package = {
                "name": package_name,
                "versionInfo": str(package_version),
                "licenseConcluded": self.remove_enclosed_parentheses(per_file_info[1]),
                "licenseDeclared": self.remove_enclosed_parentheses(per_file_info[2]),
                "copyrightText": per_file_info[3],
                "downloadLocation": str(per_file_info[4]).replace("\"", "")
            }
            self.append_package(package)

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
            for index, value in enumerate(extracted_license_info):
                if value is None:
                    extracted_license_info[index] = ''

            extracted_license = {
                "identifier": extracted_license_info[0],
                "extractedText": extracted_license_info[1],
                "licenseName": extracted_license_info[2],
            }
            self.doc["extracted_license"].append(extracted_license)
