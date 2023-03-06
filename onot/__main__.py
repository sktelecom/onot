#!/usr/bin/env python3

# SPDX-FileCopyrightText: Copyright 2022 SK TELECOM CO., LTD. <haksung@sk.com>
# SPDX-License-Identifier: Apache-2.0

from onot.tools import create_notice
from onot.log import log_setting


def main():
    log_setting.init()
    create_notice.main()


if __name__ == '__main__':
    main()