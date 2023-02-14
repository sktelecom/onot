#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright 2022 SK TELECOM CO., LTD. <haksung@sk.com>
# SPDX-FileCopyrightText: Copyright (c) 2022 Kakao Corp. https://www.kakaocorp.com
#
# SPDX-License-Identifier: Apache-2.0

import logging
import os.path

from PyQt6 import QtCore
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QDesktopServices, QFileSystemModel
from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton, QTreeView, QStackedWidget

logger = logging.getLogger("root")

class MessageWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()
        self.setLayout(layout)

        self.text_label_result = QLabel("", self)
        layout.addWidget(self.text_label_result, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_go_home = QPushButton("Go home", self)
        self.btn_go_home.setFixedWidth(180)
        layout.addWidget(self.btn_go_home, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)

    def set_message(self, msg):
        self.text_label_result.setText(msg)

class FileTreeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()
        self.setLayout(layout)

        self.model = QFileSystemModel()

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setColumnWidth(0, 400)
        self.tree.setAlternatingRowColors(True)
        self.tree.doubleClicked.connect(lambda index: QDesktopServices.openUrl(QUrl.fromLocalFile(self.model.filePath(index))))
        layout.addWidget(self.tree, 0, 0, 1, 2)

        self.btn_open_notice = QPushButton("Open", self)
        self.btn_open_notice.setFixedWidth(180)
        self.btn_open_notice.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(self.model.filePath(self.tree.currentIndex()))))
        layout.addWidget(self.btn_open_notice, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_go_home = QPushButton("Go home", self)
        self.btn_go_home.setFixedWidth(180)
        layout.addWidget(self.btn_go_home, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)

    def add_notice_path_and_show(self, notice_path):
        self.notice_path = notice_path
        dir_path = os.path.dirname(self.notice_path)
        self.model.setRootPath(dir_path)
        self.tree.setRootIndex(self.model.index(dir_path))
        self.tree.setCurrentIndex(self.model.index(self.notice_path))
        self.model.directoryLoaded.connect(lambda: self.tree.scrollTo(self.tree.currentIndex()))


class FinishWidget(QWidget):
    signal_go_home = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QGridLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(self.layout)

        self.central_widget = QStackedWidget()
        self.layout.addWidget(self.central_widget)

        self.widget_message = MessageWidget()
        self.widget_message.btn_go_home.clicked.connect(self.signal_go_home)
        self.central_widget.addWidget(self.widget_message)

        self.widget_file_tree = FileTreeWidget()
        self.widget_file_tree.btn_go_home.clicked.connect(self.signal_go_home)
        self.central_widget.addWidget(self.widget_file_tree)

    def change_file_path_name(self, file_path_name):
        self.widget_file_tree.add_notice_path_and_show(file_path_name)
        self.central_widget.setCurrentWidget(self.widget_file_tree)

    def show_message(self, msg):
        self.widget_message.set_message(msg)
        self.central_widget.setCurrentWidget(self.widget_message)