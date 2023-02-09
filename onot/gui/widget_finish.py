#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright 2022 SK TELECOM CO., LTD. <haksung@sk.com>
# SPDX-FileCopyrightText: Copyright (c) 2022 Kakao Corp. https://www.kakaocorp.com
#
# SPDX-License-Identifier: Apache-2.0

import logging

from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton

logger = logging.getLogger("root")

class FinishWidget(QWidget):
    def __init__(self, file_path_name=""):
        super().__init__()
        self.file_path_name = file_path_name
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()
        self.setLayout(layout)

        self.btn_go_home = QPushButton("Go home", self)
        layout.addWidget(self.btn_go_home, 0, 0)

        self.text_label_selected_input_file = QLabel(self.file_path_name, self)
        layout.addWidget(self.text_label_selected_input_file, 1, 0)

    def change_file_path_name(self, file_path_name):
        self.file_path_name = file_path_name
        self.text_label_selected_input_file.setText(self.file_path_name)
