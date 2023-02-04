#!/usr/bin/env python3

# SPDX-FileCopyrightText: Copyright 2022 SK TELECOM CO., LTD. <haksung@sk.com>
# SPDX-License-Identifier: Apache-2.0

import setuptools

VERSION = '0.0.2'

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="onot",
    version=VERSION,
    author="Haksung Jang",
    author_email="hakssung@gmail.com",
    description="Generate open source software notice based on the SPDX document",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sktelecom/onot",
    packages=setuptools.find_packages(),
    install_requires=[
        'click',
        'openpyxl',
        'pandas',
        'requests',
    ],
    entry_points={
        "console_scripts": [
            "onot=onot.__main__:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)