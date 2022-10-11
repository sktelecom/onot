#!/usr/bin/env python3

# SPDX-FileCopyrightText: Copyright 2022 SK TELECOM CO., LTD. <haksung@sk.com>
# SPDX-License-Identifier: Apache-2.0
import os
from onot.generating.html_resource import *
from datetime import datetime

class Generator():

    def __init__(self):
        print("debug:" + "Html class")
    
    def make_html_code(self, doc):
        title = doc['name']
        intro = 'A portion of this ' +  \
            doc['creationInfo']['organization'] + \
            ' product contains open source software, which is used and distributed in accordance with the specific license under which the open source software is distributed. A list of such open source software and the corresponding license terms is as follows:'
        head = DOCTYPE + XMLNS + HEAD + STYLE_CSS 
        body_title = BODY_TABLE_1 + title
        body_intro = BODY_TABLE_2 + intro
        
        # component info field
        body_component = COMPONENT_TITLE
        for component in doc['packages']:
            name_version = component['name'] + ' ' + str(component['versionInfo'])
            body_component += TABLE_ROW_1
            body_component += '<div id="' + name_version.replace(' ', '_') + '"></div>'
            body_component += """
                <a href="
                """ + component['downloadLocation']+ """ 
                " target="_blank">
                """ + name_version + "</a>"
            body_component += TABLE_ROW_2
            body_component += '<a href="#' + str(component['licenseConcluded']) + '">' + str(component['licenseConcluded']) + '</a>'
            body_component += TABLE_ROW_3
            body_component += str(component['copyrightText'])
            body_component += TABLE_CLOSE

        # license text field
        body_license = LICENSE_TITLE
        for license in doc['licenses']:
            body_license += '<h6><a id="' + license['licenseId'] + '">' + license['name'] + '</a></h6>'
            # component list
            body_license += '<ul>'
            for package in license['packages']:
                name_version = ' '.join(package)
                body_license += '<li>' + '<a href = "#' + name_version.replace(' ', '_') + '">' + name_version + '</a></li>'
            body_license += '</ul>'
            # license text
            license_text = ''
            # if license['licenseTextHtml'] is None:
            #     license_text = license['licenseText'].replace('\n', '<br>')
            # else:
            #     license_text = license['licenseTextHtml']
            license_text = license['licenseText'].replace('\n', '<br>')
            body_license += '<p>' + license_text + '</p><br />'
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

        return head + body_title + body_intro + body_component + body_license + body_offer + body_closing + footer

    def generate_html_file(self, doc, html_code):
        now = datetime.now()
        date_time = now.strftime("%Y%m%d_%H%M%S")
        name = doc['name'].replace(' ', '_')
        filename = 'OSS_Notice_' + doc['name'].replace(' ', '_') + '_' + date_time + '.html'
        filepathname = os.path.join('output', filename)
        f = open(filepathname, 'w')
        f.write(html_code)
        f.close()
        print("debug: output is here - " + str(filepathname))

    def generate(self, doc):
        html_code = self.make_html_code(doc)
        self.generate_html_file(doc, html_code)
        print("debug: " + "generate completed")