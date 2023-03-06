#!/usr/bin/env python3

# SPDX-FileCopyrightText: Copyright 2022 SK TELECOM CO., LTD. <haksung@sk.com>
# SPDX-License-Identifier: Apache-2.0

import logging

def init():
    logger = logging.getLogger("root")
    logger.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s:%(module)s:%(levelname)s:%(message)s", "%Y-%m-%d %H:%M:%S")
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
