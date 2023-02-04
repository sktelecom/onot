#!/usr/bin/env python3

# SPDX-FileCopyrightText: Copyright 2022 SK TELECOM CO., LTD. <haksung@sk.com>
# SPDX-License-Identifier: Apache-2.0
from onot.parsing import excel
from onot.parsing import rdf_xml

def parse_file(infile):
    print("debug: " + "parse_file - " + infile)
    if infile.endswith(".xls") or infile.endswith(".xlsx"):
        parsing_module = excel
    elif infile.endswith(".rdf") or infile.endswith(".rdf.xml"):
        parsing_module = rdf_xml
    else:
        raise Exception("FileType Not Supported" + str(infile))
    
    p = parsing_module.Parser(infile)
    return p.parse(infile)
    # with open(infile) as f:
    #     return p.parse(f)
    