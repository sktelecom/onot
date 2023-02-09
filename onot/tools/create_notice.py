#!/usr/bin/env python3
import logging

# SPDX-FileCopyrightText: Copyright 2022 SK TELECOM CO., LTD. <haksung@sk.com>
# SPDX-License-Identifier: Apache-2.0

import click
from onot.parsing.parse import parse_file
from onot.generating.generate import generate_notice

# override the help option so that you can also see help with -h
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CONTEXT_SETTINGS, help="This creates an OSS Notice file based don the excel format SPDX document.\n ex) onot -i sample/SPDXRdfExample-v2.1.xlsx -o html")
# @click.argument('input')
@click.option('-i', '--input', type=click.STRING, required=True, help="Write the input file name.")
@click.option('-o', '--output_format', type=click.STRING, required=True, help="Write the output file format.")
def main(input, output_format):
    """
    This creates the packages of the spdx document as oss notice.

    Params
    ----------
    input: str
        excel format spdx document file name
    html_format: bool
        if True, only create html format oss notice
    text_format: bool
        if True, only create text format oss notice
    """
    logger = logging.getLogger()
    logger.debug('called create')
    logger.debug("input - " + input)
    logger.debug("output - " + output_format)

    if output_format != 'html': 
        logger.warning("Sorry! Current version only supports html type output.")
    else:
        # parse excel file
        doc = parse_file(input)

        # generate html format oss notice
        generate_notice(doc, 'html')

if __name__ == "__main__":
    main()