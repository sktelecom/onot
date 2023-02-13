#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright 2022 SK TELECOM CO., LTD. <haksung@sk.com>
# SPDX-FileCopyrightText: Copyright (c) 2022 Kakao Corp. https://www.kakaocorp.com
#
# SPDX-License-Identifier: Apache-2.0

import logging
import sys

from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QStackedWidget, QMainWindow

from onot.gui.widget_finish import FinishWidget
from onot.gui.widget_home import HomeWidget
from onot.gui.widget_progress import ProgressWidget
from onot.log import log_setting

logger = logging.getLogger("root")


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("onot")
        self.setGeometry(600, 300, 600, 200)
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.widget_home = HomeWidget()
        self.widget_home.btn_start.clicked.connect(self.start)
        self.central_widget.addWidget(self.widget_home)

        self.widget_progress = ProgressWidget()
        self.widget_progress.signal_stop.connect(self.stop)
        self.widget_progress.signal_finish.connect(self.finish)
        self.widget_progress.signal_exception.connect(self.handle_exception)
        self.central_widget.addWidget(self.widget_progress)

        self.widget_finish = FinishWidget()
        self.widget_finish.signal_go_home.connect(self.go_home)
        self.central_widget.addWidget(self.widget_finish)

    def start(self):
        self.central_widget.setCurrentWidget(self.widget_progress)
        file = self.widget_home.text_label_selected_input_file.text()
        output_format = self.widget_home.combo_box_select_output_format.currentText()
        self.widget_progress.create_notice(file, output_format)

    @QtCore.pyqtSlot(str)
    def stop(self, msg):
        self.widget_finish.show_message(str(msg))
        self.central_widget.setCurrentWidget(self.widget_finish)

    @QtCore.pyqtSlot(str)
    def finish(self, msg):
        self.setGeometry(600, 300, 600, 400)
        self.widget_finish.change_file_path_name(msg)
        self.central_widget.setCurrentWidget(self.widget_finish)

    @QtCore.pyqtSlot(Exception)
    def handle_exception(self, exception):
        self.widget_finish.show_message(str(exception))
        self.central_widget.setCurrentWidget(self.widget_finish)

    @QtCore.pyqtSlot()
    def go_home(self):
        self.setGeometry(600, 300, 600, 200)
        self.central_widget.setCurrentWidget(self.widget_home)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    log_setting.init()
    main()