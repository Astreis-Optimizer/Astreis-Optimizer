# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'right_columntfojJZ.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class UI_RightColumn:
    def setup_ui(self, parent):
        if not parent.objectName():
            parent.setObjectName("RightColumn")

        # MAIN LAYOUT
        self.main_layout = QVBoxLayout(parent)
        self.main_layout.setContentsMargins(5, 0, 5, 5)
        self.main_layout.setSpacing(0)

        # CONTENT FRAME
        self.content_frame = QFrame()
        self.content_frame.setStyleSheet("background: none")

        # Content Layout
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        self.content_layout.setSpacing(5)

        # Add content frame to main layout
        self.main_layout.addWidget(self.content_frame)

    # Removed retranslateUi and header references

