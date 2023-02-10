#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright 2022 SK TELECOM CO., LTD. <haksung@sk.com>
# SPDX-FileCopyrightText: Copyright (c) 2022 Kakao Corp. https://www.kakaocorp.com
#
# SPDX-License-Identifier: Apache-2.0

import logging
import os.path

from PyQt6.QtCore import QUrl, QDir, QItemSelectionModel, QTimer
from PyQt6.QtGui import QDesktopServices, QFileSystemModel, QCursor
from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton, QTreeView

logger = logging.getLogger("root")


class FinishWidget(QWidget):
    def __init__(self, file_path_name=""):
        super().__init__()
        self.init_ui()
        self.notice_path = ""

    def init_ui(self):
        layout = QGridLayout()
        self.setLayout(layout)


        self.text_label_result = QLabel("", self)
        layout.addWidget(self.text_label_result, 1, 0)

        self.model = QFileSystemModel()

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setColumnWidth(0, 400)
        self.tree.setAlternatingRowColors(True)
        self.tree.doubleClicked.connect(lambda index: QDesktopServices.openUrl(QUrl("file://" + self.model.filePath(index))))
        layout.addWidget(self.tree)

        self.btn_go_home = QPushButton("Go home", self)
        layout.addWidget(self.btn_go_home, 0, 1)

        self.btn_open_notice = QPushButton("Open", self)
        self.btn_open_notice.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("file://" + self.model.filePath(self.tree.currentIndex()))))
        layout.addWidget(self.btn_open_notice, 0, 0)

    def change_file_path_name(self, file_path_name):
        self.notice_path = file_path_name
        dir_path = os.path.dirname(self.notice_path)
        self.model.setRootPath(dir_path)
        self.tree.setRootIndex(self.model.index(dir_path))
        self.tree.setCurrentIndex(self.model.index(self.notice_path))
        self.model.directoryLoaded.connect(lambda: self.tree.scrollToBottom())

        self.text_label_result.setText(self.notice_path)
