#!/usr/bin/env python3

# SPDX-FileCopyrightText: Copyright 2022 SK TELECOM CO., LTD. <haksung@sk.com>
# SPDX-FileCopyrightText: Copyright (c) 2022 Kakao Corp. https://www.kakaocorp.com
#
# SPDX-License-Identifier: Apache-2.0

import os
import sys
import logging
from datetime import datetime

logger = logging.getLogger("root")

class Generator():

    def __init__(self):
        logger.debug("text class")

    def make_text(self, doc):
        title = 'OSS Notice for ' + doc['name']

        intro = 'A portion of this ' + \
            doc['creationInfo']['organization'] + \
            ' product contains open source software, which is used and distributed in accordance with the specific license under which the open source software is distributed. A list of such open source software and the corresponding license terms is as follows:'

        components = ''
        for component in doc['packages']:
            components += component['name'] + ' ' + str(component['versionInfo']) + "\n"
            components += '  ' + component['licenseConcluded'] + '\n\n'

        copyright_data = ''
        for copyright in doc['packages']:
            copyright_data += copyright['name'] + ' ' + str(copyright['versionInfo']) + "\n"
            copyright_data += '  ' + str(copyright['copyrightText']) + '\n\n'

        licenses = ''
        for license in doc['licenses']:
            licenses += license['name'] + '\n'
            # component list
            for index, package in enumerate(license['packages']):
                if index == 0:
                    licenses += '('
                licenses += ' '.join(package).strip()

                packages_len = len(license['packages'])
                if index < packages_len - 1:
                    licenses += ', '
                if index == packages_len - 1:
                    licenses += ')\n\n\n'
            licenses += license['licenseText'].strip('\n') + '\n\n\n'

        writer = 'Offer of Source Code\n\n'
        email = doc['creationInfo']['email']
        writer += 'This product includes software code developed by third parties, including software code subject to the GNU General Public License ("GPL") or GNU Lesser General Public License ("LGPL"). Where such specific license terms entitle you to the source code of such software, we will provide upon written request the applicable GPL and LGPL source code files via CD-ROM for a nominal cost to cover shipping and media charges as allowed under the GPL and LGPL. Please direct all inquiries to '
        writer += email + '. You may obtain the complete Corresponding Source code from us for a period of three years after our last shipment of this product. This offer is valid to anyone in receipt of this information. '
        if 'sourceDownloadUrl' in doc['creationInfo']:
            sourceDownloadUrl = doc['creationInfo']['sourceDownloadUrl']
            writer += 'You may also find the source code at ' + sourceDownloadUrl

        closing = 'If you have any questions regarding open source software contained in this product, please contact '
        closing += email + '.'

        return title + '\n\n' + '='*40 + '\n\n' + \
            intro + '\n\n' + \
            components + '-'*40 + '\n\n' + \
            'Copyright Data\n\n' + copyright_data + '-'*40 + '\n\n' + \
            'Licenses\n\n' + licenses + '-'*40 + '\n\n' + \
            writer + '\n\n' + closing + '\n\n' + '='*40 + '\n\n' + \
            'Copyright ' + str(datetime.today().year) + ' SK TELECOM CO., LTD.'

    def generate_text_file(self, doc, text):
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

        file_name = 'OSS_Notice_' + doc['name'].replace(' ', '_') + '_' + date_time + '.txt'
        file_path_name = os.path.join(directory_name, file_name)
        f = open(file_path_name, 'w', encoding='UTF-8')
        f.write(text)
        f.close()
        logger.debug("output is here - " + str(file_path_name))
        return file_path_name

    def generate(self, doc):
        text = self.make_text(doc)
        file_path_name = self.generate_text_file(doc, text)
        logger.debug("generate completed")
        return file_path_name
