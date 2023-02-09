#!/usr/bin/env python3

# SPDX-FileCopyrightText: Copyright 2022 SK TELECOM CO., LTD. <haksung@sk.com>
# SPDX-License-Identifier: Apache-2.0
from onot.generating import html

def generate_notice(doc, ext):
    if ext == 'html':
        file_type = html
    g = file_type.Generator()
    return g.generate(doc)
    