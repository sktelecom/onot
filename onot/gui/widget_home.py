#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright 2022 SK TELECOM CO., LTD. <haksung@sk.com>
# SPDX-FileCopyrightText: Copyright (c) 2022 Kakao Corp. https://www.kakaocorp.com
#
# SPDX-License-Identifier: Apache-2.0

import logging

from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton, QFileDialog, \
    QComboBox

logger = logging.getLogger("root")

class HomeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(30)
        self.setLayout(layout)

        self.text_label_selected_input_file = QLabel("", self)
        layout.addWidget(self.text_label_selected_input_file, 0, 0)


        self.btn_select_input_file = QPushButton("Select input file", self)
        self.btn_select_input_file.clicked.connect(self.open_selection_window)
        self.btn_select_input_file.setFixedWidth(180)
        layout.addWidget(self.btn_select_input_file, 0, 1)

        self.text_label_output_format = QLabel("Output format: ")
        layout.addWidget(self.text_label_output_format, 1, 0)

        self.combo_box_select_output_format = QComboBox(self)
        self.combo_box_select_output_format.addItems(["html"])
        self.combo_box_select_output_format.setFixedWidth(180)
        self.combo_box_select_output_format.setEditable(True)
        self.combo_box_select_output_format.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.combo_box_select_output_format.lineEdit().setReadOnly(True)
        layout.addWidget(self.combo_box_select_output_format, 1, 1)

        self.btn_start = QPushButton("Start")
        self.btn_start.setFixedWidth(120)
        layout.addWidget(self.btn_start, 2, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)


    def open_selection_window(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open file', './')
        if file_name[0]:
            self.text_label_selected_input_file.setText(file_name[0])