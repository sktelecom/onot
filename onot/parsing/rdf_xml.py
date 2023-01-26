#!/usr/bin/env python3
import pprint

# SPDX-FileCopyrightText: Copyright 2022 SK TELECOM CO., LTD. <haksung@sk.com>
# SPDX-FileCopyrightText: Copyright (c) 2022 Kakao Corp. https://www.kakaocorp.com
#
# SPDX-License-Identifier: Apache-2.0

import os
import re
from rdflib import Graph
from rdflib import Namespace
from rdflib import RDF
from rdflib.term import Literal
from rdflib.term import URIRef
from rdflib.term import BNode
from onot.parsing import spdx_license

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

class Parser():
    def __init__(self, file):
        print("debug:" + "RDF/XML Parser class")
        self.graph = Graph().parse(source=file, format="xml")
        self.spdx_namespace = Namespace("http://spdx.org/rdf/terms#")
        self.doc = {}
        self.packages = []
        self.licenses = []
        self.extracted_licenses = []

    def validate_sheet(self, file):
        print("debug: ")

    def validate_predicates_exist(self, subject, predicates):
        # validate necessary predicate are existed
        for predicate in predicates:
            if not (subject, self.spdx_namespace[predicate], None) in self.graph:
                raise ValueError("required predicate is not existed: " + self.spdx_namespace[predicate])

    def remove_parentheses_if_enclosed_parentheses(self, expression):
        # if the overall expression is enclosed in parentheses, remove the parentheses.
        if str(expression).startswith("(") and str(expression).endswith(")"):
            return expression[1:len(expression)-1]
        return expression

    def extract(self, subject, predicates):

        def extract_license_expression(object):
            if "noassertion" in str(object).lower():
                return ""
            if type(object) == Literal:
                return str(object)
            elif type(object) == URIRef:
                basename = os.path.basename(object)
                return basename.split("#")[1] if "#" in basename else basename
            # If the object is BNode(Blank Node), there are more than two objects.
            # https://rdflib.readthedocs.io/en/stable/rdf_terms.html#bnodes
            elif type(object) == BNode:
                license_expression = ""
                operator = ""

                for _, _, tag_name in self.graph.triples((object, RDF.type, None)):
                    operator_tag = str(os.path.basename(tag_name)).split("#")[1]
                    operator = LICENSE_COMPOSITE_OPERATORS[operator_tag]

                for _, _, o in self.graph.triples((object, self.spdx_namespace["member"], None)):
                    license_expression = license_expression + extract_license_expression(o) + operator

                for _, _, o in self.graph.triples((object, self.spdx_namespace["licenseException"], None)):
                    license_expression = license_expression + extract_license_expression(o) + operator

                return license_expression[:-len(operator)] if operator == " WITH " else "(" + license_expression[:-len(operator)] + ")"

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
                    license_expression = extract_license_expression(o)
                    objects.append(self.remove_parentheses_if_enclosed_parentheses(license_expression))
                    # extracted[predicate] = extract_license_expression(o)
                elif "noassertion" in str(o).lower():
                    objects.append("")
                    # extracted[predicate] = ""
                elif type(o) == BNode:
                    objects.append(o)
                    # extracted[predicate] = o
                else:
                    objects.append(str(o).replace("\n", "").strip())
                    # extracted[predicate] = str(o).replace("\n", "").strip()
            objects = objects[0] if len(objects) == 1 else objects
            extracted[predicate] = objects
        return extracted

    def append_package(self, package_to_be_appended):
        # Check if there are duplicate packages already appended
        if any(package["name"] == package_to_be_appended["name"] and package["versionInfo"] == package_to_be_appended[
            "versionInfo"] for package in self.packages):
            return
        self.packages.append(package_to_be_appended)


    def extract_license_ids(self, licenses):
        def extract_license_id_from_url(license_url):
            basename = os.path.basename(license_url)
            return basename.split("#")[1] if "#" in basename else basename

        if type(licenses) == list:
            return list(map(extract_license_id_from_url, licenses))

        return extract_license_id_from_url(licenses)

    def document_info(self):
        # get document name
        for document_id, _, _ in self.graph.triples((None, RDF.type, self.spdx_namespace["SpdxDocument"])):
            self.validate_predicates_exist(document_id, [PREDICATE_DOCUMENT_NAME])
            document_info = self.extract(document_id, [PREDICATE_DOCUMENT_NAME])
            self.doc["name"] = document_info[PREDICATE_DOCUMENT_NAME]

        # get organization & email
        for creator_node, _, _ in self.graph.triples((None, RDF.type, self.spdx_namespace["CreationInfo"])):
            self.validate_predicates_exist(creator_node, [PREDICATE_DOCUMENT_CREATOR])
            creators = self.extract(creator_node, [PREDICATE_DOCUMENT_CREATOR])
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

        return True

    def package_info(self):
        predicates_of_package = [
            PREDICATE_PACKAGE_NAME,
            PREDICATE_PACKAGE_VERSION_INFO,
            PREDICATE_PACKAGE_LICENSE_CONCLUDED,
            PREDICATE_PACKAGE_LICENSE_DECLARED,
            PREDICATE_PACKAGE_COPYRIGHT_TEXT,
            PREDICATE_PACKAGE_DOWNLOAD_LOCATION
        ]

        for package_id, _, _ in self.graph.triples((None, RDF.type, self.spdx_namespace["Package"])):
            self.validate_predicates_exist(package_id, predicates_of_package)
            package_info = self.extract(package_id, predicates_of_package)
            package = {
                PREDICATE_PACKAGE_NAME: package_info[PREDICATE_PACKAGE_NAME],
                PREDICATE_PACKAGE_VERSION_INFO: package_info[PREDICATE_PACKAGE_VERSION_INFO],
                PREDICATE_PACKAGE_LICENSE_CONCLUDED: self.extract_license_ids(package_info[PREDICATE_PACKAGE_LICENSE_CONCLUDED]),
                PREDICATE_PACKAGE_LICENSE_DECLARED: self.extract_license_ids(package_info[PREDICATE_PACKAGE_LICENSE_DECLARED]),
                PREDICATE_PACKAGE_COPYRIGHT_TEXT: package_info[PREDICATE_PACKAGE_COPYRIGHT_TEXT],
                PREDICATE_PACKAGE_DOWNLOAD_LOCATION: package_info[PREDICATE_PACKAGE_DOWNLOAD_LOCATION]
            }
            self.append_package(package)


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

    def per_file_info(self):
        predicates_of_file = [
            PREDICATE_FILE_NAME,
            PREDICATE_FILE_LICENSE_CONCLUDED,
            PREDICATE_FILE_LICENSE_DECLARED,
            PREDICATE_FILE_COPYRIGHT_TEXT,
            # PREDICATE_FILE_DOWNLOAD_LOCATION
        ]

        for file_id, _, _ in self.graph.triples((None, RDF.type, self.spdx_namespace["File"])):
            self.validate_predicates_exist(file_id, predicates_of_file)
            file_info = self.extract(file_id, predicates_of_file)

            package_name, package_version = self.extract_package_name_and_package_version(file_info[PREDICATE_FILE_NAME])
            package = {
                PREDICATE_PACKAGE_NAME: package_name,
                PREDICATE_PACKAGE_VERSION_INFO: package_version,
                PREDICATE_PACKAGE_LICENSE_CONCLUDED: self.extract_license_ids(file_info[PREDICATE_FILE_LICENSE_CONCLUDED]),
                PREDICATE_PACKAGE_LICENSE_DECLARED: self.extract_license_ids(file_info[PREDICATE_FILE_LICENSE_DECLARED]),
                PREDICATE_PACKAGE_COPYRIGHT_TEXT: file_info[PREDICATE_FILE_COPYRIGHT_TEXT],
                PREDICATE_PACKAGE_DOWNLOAD_LOCATION: ""
            }
            self.append_package(package)
        self.doc["packages"] = self.packages

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

    def extracted_license_info(self):
        predicates_of_license = [
            PREDICATE_LICENSE_ID,
            PREDICATE_LICENSE_NAME,
            PREDICATE_LICENSE_EXTRACTED_TEXT
        ]

        for license_id, _, _ in self.graph.triples((None, RDF.type, self.spdx_namespace["ExtractedLicensingInfo"])):
            self.validate_predicates_exist(license_id, predicates_of_license)
            license_info = self.extract(license_id, predicates_of_license)
            license = {
                "identifier": license_info[PREDICATE_LICENSE_ID],
                "licenseName":  license_info[PREDICATE_LICENSE_NAME] if PREDICATE_LICENSE_NAME in license_info else "",
                "extractedText": license_info[PREDICATE_LICENSE_EXTRACTED_TEXT]
            }
            self.extracted_licenses.append(license)
        self.doc["extracted_license"] = self.extracted_licenses

    def get_details_license(self, license_name):
        sl = spdx_license.SPDX_License()

        # check whether the licenseId is existed in the spdx license list
        details_url = sl.get_spdx_license_detailsUrl(license_name)
        print("debug: " + str(details_url))
        if details_url is not None:
            # if so, get the license text from spdx repo : "https://spdx.org/licenses/[LICENSE_ID].json"
            details_license = sl.get_spdx_license_details(details_url)
        else:
            # if not, get the license text from External Refs sheet
            if "extracted_license" not in self.doc:
                self.extracted_license_info()

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
        for package in self.packages:
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

        # License info
        self.license_info()

        return self.doc

    def parse(self, file):
        print("debug: " + "parse")

        self.validate_sheet(file)
        doc = self.load_doc(file)
        return doc
