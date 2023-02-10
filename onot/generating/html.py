#!/usr/bin/env python3

# SPDX-FileCopyrightText: Copyright 2022 SK TELECOM CO., LTD. <haksung@sk.com>
# SPDX-FileCopyrightText: Copyright (c) 2022 Kakao Corp. https://www.kakaocorp.com
#
# SPDX-License-Identifier: Apache-2.0

import os
import re
import sys
import logging
from datetime import datetime
from onot.generating.html_resource import *

logger = logging.getLogger("root")

class Generator():

    def __init__(self):
        logger.debug("Html class")

    def convert_license_expression(self, license_name):
        splited = re.split(r'OR|AND|WITH', str(license_name))
        licenses = list(map(lambda license: license.replace("(", "").replace(")", "").strip(), splited))
        license_component = license_name
        for license in licenses:
            license_component = str(license_component).replace(str(license), '<a href="#' + str(license) + '">' + str(license) + '</a>')
        return license_component

    def convert_download_location(self, download_location, name_version):
        if download_location == "":
            return name_version
        else:
            return """
                <a href="
                """ + download_location + """ 
                " target="_blank">
                """ + name_version + "</a>"

    def make_html_code(self, doc):
        title = doc['name']
        intro = 'A portion of this ' +  \
            doc['creationInfo']['organization'] + \
            ' product contains open source software, which is used and distributed in accordance with the specific license under which the open source software is distributed. A list of such open source software and the corresponding license terms is as follows:'
        head = DOCTYPE + XMLNS + HEAD + STYLE_CSS
        body_title = BODY_TABLE_1 + '<h2>OSS Notice for' + title + '</h2>'
        body_intro = BODY_TABLE_2 + intro

        # component info field
        body_component = COMPONENT_TITLE
        for component in doc['packages']:
            name_version = component['name'] + ' ' + str(component['versionInfo'])
            body_component += '<tr>'
            body_component += '<td scope="row" data-label="Name" id="' + name_version.replace(' ', '_') + '">'
            body_component += self.convert_download_location(component["downloadLocation"], name_version)
            body_component += '</td>'
            body_component += '<td data-label="License">' + self.convert_license_expression(component['licenseConcluded']) + '</td>'
            body_component += '<td data-label="Copyright">' + str(component['copyrightText']) + '</td>'
            body_component += '</tr>'
        body_component_close = TABLE_CLOSE

        # license text field
        body_license = LICENSE_TITLE
        for license in doc['licenses']:
            body_license += '<div class="license">'
            body_license += '<h4 id="' + license['licenseId'] + '">' + license['name']
            # component list
            for package in license['packages']:
                name_version = ' '.join(package)
                body_license += '<a href = "#' + name_version.replace(' ', '_') + '">' + name_version + '</a>'
            body_license += '</h4>'
            body_license += '<div class="article">'
            # license text
            license_text = ''
            # if license['licenseTextHtml'] is None:
            #     license_text = license['licenseText'].replace('\n', '<br>')
            # else:
            #     license_text = license['licenseTextHtml']
            license_text = license['licenseText'].replace('\n', '<br>')
            body_license += '<p>' + license_text + '</p><br />'
            body_license += '</div>'
            body_license += '</div>'
        body_license += LICENSE_TABLE_CLOSE

        # writter
        body_offer = WRITTEN_OFFER_TITLE
        email = doc['creationInfo']['email']
        body_offer += 'This product includes software code developed by third parties, including software code subject to the GNU General Public License ("GPL") or GNU Lesser General Public License ("LGPL"). Where such specific license terms entitle you to the source code of such software, we will provide upon written request the applicable GPL and LGPL source code files via CD-ROM for a nominal cost to cover shipping and media charges as allowed under the GPL and LGPL. Please direct all inquiries to '
        body_offer += email + '. You may obtain the complete Corresponding Source code from us for a period of three years after our last shipment of this product. This offer is valid to anyone in receipt of this information.'
        body_offer += "</p>\n" + WRITTEN_OFFER_CLOSE

        # closing
        body_closing = 'If you have any questions regarding open source software contained in this product, please contact '
        body_closing += email + '.'

        # footer
        footer = FOOTER

        return head + body_title + body_intro + body_component + body_component_close + body_license + body_offer + body_closing + footer

    def generate_html_file(self, doc, html_code):
        now = datetime.now()
        date_time = now.strftime("%Y%m%d_%H%M%S")
        name = doc['name'].replace(' ', '_')

        if "/Contents" in sys.executable:
            current_path = os.path.dirname(sys.executable.split("/Contents")[0])
            directory_name = os.path.join(current_path, "output")
        else:
            directory_name = os.path.abspath("output")

        if not os.path.exists(directory_name):
            os.makedirs(directory_name)

        file_name = 'OSS_Notice_' + doc['name'].replace(' ', '_') + '_' + date_time + '.html'
        file_path_name = os.path.join(directory_name, file_name)
        f = open(file_path_name, 'w', encoding='UTF-8')
        f.write(html_code)
        f.close()
        logger.debug("output is here - " + str(file_path_name))
        return file_path_name

    def generate(self, doc):
        html_code = self.make_html_code(doc)
        file_path_name = self.generate_html_file(doc, html_code)
        logger.debug("generate completed")
        return file_path_name
