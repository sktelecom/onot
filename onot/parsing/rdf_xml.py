#!/usr/bin/env python3

# SPDX-FileCopyrightText: Copyright 2022 SK TELECOM CO., LTD. <haksung@sk.com>
# SPDX-FileCopyrightText: Copyright (c) 2022 Kakao Corp. https://www.kakaocorp.com
#
# SPDX-License-Identifier: Apache-2.0

import os
from rdflib import Graph, Namespace, RDF
from rdflib.term import Literal, URIRef, BNode
import logging
from onot.parsing import parser

SUBJECT_DOCUMENT = "SpdxDocument"
SUBJECT_PACKAGE = "Package"
SUBJECT_FILE = "File"
SUBJECT_EXTRACTED_LICENSE = "ExtractedLicensingInfo"

PREDICATE_DOCUMENT_NAME = "name"
PREDICATE_DOCUMENT_CREATOR = "creator"

PREDICATE_PACKAGE_NAME = "name"
PREDICATE_PACKAGE_VERSION_INFO = "versionInfo"
PREDICATE_PACKAGE_LICENSE_CONCLUDED = "licenseConcluded"
PREDICATE_PACKAGE_LICENSE_DECLARED = "licenseDeclared"
PREDICATE_PACKAGE_COPYRIGHT_TEXT = "copyrightText"
PREDICATE_PACKAGE_DOWNLOAD_LOCATION = "downloadLocation"

PREDICATE_FILE_NAME = "fileName"
PREDICATE_FILE_LICENSE_CONCLUDED = "licenseConcluded"
PREDICATE_FILE_LICENSE_DECLARED = "licenseInfoInFile"
PREDICATE_FILE_COPYRIGHT_TEXT = "copyrightText"
PREDICATE_FILE_DOWNLOAD_LOCATION = ""

PREDICATE_LICENSE_ID = "licenseId"
PREDICATE_LICENSE_NAME = "name"
PREDICATE_LICENSE_EXTRACTED_TEXT = "extractedText"

LICENSE_COMPOSITE_OPERATORS = {
    "DisjunctiveLicenseSet": " OR ",
    "ConjunctiveLicenseSet": " AND ",
    "WithExceptionOperator": " WITH "
}

logger = logging.getLogger("root")

class Parser(parser.AbstractParser):
    def __init__(self, file):
        logger.debug("RDF/XML Parser class")
        super().__init__()
        self.graph = Graph().parse(source=file, format="xml")
        self.spdx_namespace = Namespace("http://spdx.org/rdf/terms#")

    def validate_file(self, file):
        # validate file contents : all necessary information should be in the file.
        # subject & predicates
        # 1. SpdxDocument Subject
        # - name
        # - creator (Organization / Email)
        # 2. Package Subject
        # - name
        # - versionInfo
        # - downloadLocation
        # - licenseConcluded
        # - licenseDeclared
        # - copyrightText
        # 3. File Subject
        # - fileName
        # - licenseConcluded
        # - licenseInfoInFile
        # - copyrightText
        # - downloadLocation
        required_subjects = [
            SUBJECT_DOCUMENT,
            SUBJECT_PACKAGE,
            SUBJECT_PACKAGE,
            # SUBJECT_EXTRACTED_LICENSE
        ]
        for subject in required_subjects:
            if not (None, RDF.type, self.spdx_namespace[subject]) in self.graph:
                raise ValueError("required subject is not existed: " + subject)

    def validate_predicates_exist(self, subject, predicates):
        # validate necessary predicate are existed
        for predicate in predicates:
            if not (subject, self.spdx_namespace[predicate], None) in self.graph:
                raise ValueError("required predicate is not existed: " + self.spdx_namespace[predicate])

    def extract_license_expression(self, object):
        if type(object) == Literal:
            return str(object)
        elif type(object) == URIRef:
            # parse license name from url
            basename = os.path.basename(object)
            return basename.split("#")[1] if "#" in basename else basename
        # If the object is BNode(Blank Node), there are more than two objects.
        # https://rdflib.readthedocs.io/en/stable/rdf_terms.html#bnodes
        # This case means dual license.
        elif type(object) == BNode:
            for _, _, tag_name in self.graph.triples((object, RDF.type, None)):
                operator_tag = str(os.path.basename(tag_name)).split("#")[1]
                operator = LICENSE_COMPOSITE_OPERATORS[operator_tag]

            license_expression = ""
            for _, _, o in self.graph.triples((object, self.spdx_namespace["member"], None)):
                license_expression = license_expression + self.extract_license_expression(o) + operator

            for _, _, o in self.graph.triples((object, self.spdx_namespace["licenseException"], None)):
                license_expression = license_expression + self.extract_license_expression(o) + operator

            return license_expression[:-len(operator)] if operator == " WITH " else "(" + license_expression[:-len(operator)] + ")"

    def extract(self, subject, predicates):
        extracted = {}
        for predicate in predicates:
            objects = []
            for s, p, o in self.graph.triples((subject, self.spdx_namespace[predicate], None)):
                if predicate in [
                    PREDICATE_PACKAGE_LICENSE_CONCLUDED,
                    PREDICATE_PACKAGE_LICENSE_DECLARED,
                    PREDICATE_FILE_LICENSE_CONCLUDED,
                    PREDICATE_FILE_LICENSE_DECLARED
                ]:
                    license_expression = self.extract_license_expression(o)
                    objects.append(self.remove_enclosed_parentheses(license_expression))
                elif type(o) == BNode:
                    objects.append(o)
                else:
                    objects.append(str(o).replace("\n", "").strip())

            if len(objects) == 0:
                extracted[predicate] = ""
            elif len(objects) == 1:
                extracted[predicate] = objects[0]
            else:
                extracted[predicate] = objects
        return extracted

    def document_info(self):
        # get document name
        for subject, _, _ in self.graph.triples((None, RDF.type, self.spdx_namespace["SpdxDocument"])):
            self.validate_predicates_exist(subject, [PREDICATE_DOCUMENT_NAME])
            document_info = self.extract(subject, [PREDICATE_DOCUMENT_NAME])
            self.doc["name"] = document_info[PREDICATE_DOCUMENT_NAME]

        # get organization & email
        for subject, _, _ in self.graph.triples((None, RDF.type, self.spdx_namespace["CreationInfo"])):
            self.validate_predicates_exist(subject, [PREDICATE_DOCUMENT_CREATOR])
            creators = self.extract(subject, [PREDICATE_DOCUMENT_CREATOR])
            for creator in creators[PREDICATE_DOCUMENT_CREATOR]:
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

    def package_info(self):
        required_predicates = [
            PREDICATE_PACKAGE_NAME,
            PREDICATE_PACKAGE_VERSION_INFO,
            PREDICATE_PACKAGE_LICENSE_CONCLUDED,
            PREDICATE_PACKAGE_LICENSE_DECLARED,
            PREDICATE_PACKAGE_COPYRIGHT_TEXT,
            PREDICATE_PACKAGE_DOWNLOAD_LOCATION
        ]
        non_required_predicates = []

        for subject, _, _ in self.graph.triples((None, RDF.type, self.spdx_namespace["Package"])):
            self.validate_predicates_exist(subject, required_predicates)
            package_info = self.extract(subject, required_predicates + non_required_predicates)
            package = {
                "name": package_info[PREDICATE_PACKAGE_NAME],
                "versionInfo": package_info[PREDICATE_PACKAGE_VERSION_INFO],
                "licenseConcluded": package_info[PREDICATE_PACKAGE_LICENSE_CONCLUDED],
                "licenseDeclared": package_info[PREDICATE_PACKAGE_LICENSE_DECLARED],
                "copyrightText": package_info[PREDICATE_PACKAGE_COPYRIGHT_TEXT],
                "downloadLocation": package_info[PREDICATE_PACKAGE_DOWNLOAD_LOCATION]
            }
            self.append_package(package)

    def per_file_info(self):
        required_predicates = [
            PREDICATE_FILE_NAME,
            PREDICATE_FILE_LICENSE_CONCLUDED,
            PREDICATE_FILE_LICENSE_DECLARED,
            PREDICATE_FILE_COPYRIGHT_TEXT,
        ]
        non_required_predicates = [
            PREDICATE_FILE_DOWNLOAD_LOCATION
        ]

        for subject, _, _ in self.graph.triples((None, RDF.type, self.spdx_namespace["File"])):
            self.validate_predicates_exist(subject, required_predicates)
            file_info = self.extract(subject, required_predicates + non_required_predicates)

            package_name, package_version = self.extract_package_name_and_package_version(file_info[PREDICATE_FILE_NAME])
            package = {
                "name": package_name,
                "versionInfo": package_version,
                "licenseConcluded": file_info[PREDICATE_FILE_LICENSE_CONCLUDED],
                "licenseDeclared": file_info[PREDICATE_FILE_LICENSE_DECLARED],
                "copyrightText": file_info[PREDICATE_FILE_COPYRIGHT_TEXT],
                "downloadLocation": ""
            }
            self.append_package(package)

    def extracted_license_info(self):
        required_predicates = [
            PREDICATE_LICENSE_ID,
            PREDICATE_LICENSE_EXTRACTED_TEXT
        ]
        non_required_predicates = [
            PREDICATE_LICENSE_NAME
        ]

        for subject, _, _ in self.graph.triples((None, RDF.type, self.spdx_namespace["ExtractedLicensingInfo"])):
            self.validate_predicates_exist(subject, required_predicates)
            license_info = self.extract(subject, required_predicates + non_required_predicates)
            extracted_license = {
                "identifier": license_info[PREDICATE_LICENSE_ID],
                "licenseName":  license_info[PREDICATE_LICENSE_NAME],
                "extractedText": license_info[PREDICATE_LICENSE_EXTRACTED_TEXT]
            }
            self.doc["extracted_license"].append(extracted_license)
