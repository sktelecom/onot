#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright 2022 SK TELECOM CO., LTD. <haksung@sk.com>
# SPDX-FileCopyrightText: Copyright (c) 2022 Kakao Corp. https://www.kakaocorp.com
#
# SPDX-License-Identifier: Apache-2.0

import logging
import os
import traceback

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import QThread, Qt
from PyQt6.QtWidgets import QWidget, QGridLayout, QPushButton

from onot.generating.generate import generate_notice
from onot.parsing.parse import parse_file

logger = logging.getLogger("root")

class WidgetLogHandler(logging.Handler, QtCore.QObject):
    signal_log = QtCore.pyqtSignal(str)

    def __init__(self, widget):
        super().__init__()
        QtCore.QObject.__init__(self)
        self.setFormatter(logging.Formatter('%(asctime)s:%(module)s:%(levelname)s:%(message)s', '%Y-%m-%d %H:%M:%S'))
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        self.signal_log.emit(msg)

class CreateNoticeThread(QThread):
    signal_finish_job = QtCore.pyqtSignal(str)
    signal_exception = QtCore.pyqtSignal(Exception)

    def __init__(self, parent, input, output_format):
        super().__init__(parent)
        self.input = input
        self.output_format = output_format

    def run(self):
        try:
            # parse excel file
            doc = parse_file(self.input)

            # generate html format oss notice
            file_path_name = generate_notice(doc, self.output_format)
            self.signal_finish_job.emit(file_path_name)
        except Exception as ex:
            logger.error(ex)
            logger.debug(traceback.format_exc())
            self.signal_exception.emit(ex)


class ProgressWidget(QWidget):
    signal_stop = QtCore.pyqtSignal(str)
    signal_finish = QtCore.pyqtSignal(str)
    signal_exception = QtCore.pyqtSignal(Exception)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        self.log_text_box = QtWidgets.QPlainTextEdit(self)
        self.log_text_box.setReadOnly(True)
        layout.addWidget(self.log_text_box, 0, 0)

        logger_handler = WidgetLogHandler(self.log_text_box)
        logger_handler.signal_log.connect(lambda text: [
            self.log_text_box.appendPlainText(text),
            self.log_text_box.verticalScrollBar().setValue(self.log_text_box.verticalScrollBar().maximum())
        ])
        logger.addHandler(logger_handler)

        self.btn_stop_job = QPushButton("Stop", self)
        self.btn_stop_job.setFixedWidth(180)
        self.btn_stop_job.clicked.connect(self.stop_job)
        layout.addWidget(self.btn_stop_job, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)

    def create_notice(self, input, output_format):
        self.job = CreateNoticeThread(self, input, output_format)
        self.job.signal_finish_job.connect(self.finish_create_notice)
        self.job.signal_exception.connect(self.handle_exception)
        self.job.start()

    def stop_job(self):
        self.log_text_box.clear()
        self.job.terminate()
        self.job.signal_finish_job.disconnect()
        self.job.signal_exception.disconnect()
        self.signal_stop.emit("It has been stopped.")

    @QtCore.pyqtSlot(str)
    def finish_create_notice(self, msg):
        self.log_text_box.clear()
        self.signal_finish.emit(msg)

    @QtCore.pyqtSlot(Exception)
    def handle_exception(self, exception):
        self.log_text_box.clear()
        self.signal_exception.emit(exception)