# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_pagesigKGOg.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QSizePolicy,
    QStackedWidget, QVBoxLayout, QWidget)

class Ui_MainPages(object):
    def setupUi(self, MainPages):
        if not MainPages.objectName():
            MainPages.setObjectName(u"MainPages")
        MainPages.resize(860, 600)
        self.main_pages_layout = QVBoxLayout(MainPages)
        self.main_pages_layout.setSpacing(0)
        self.main_pages_layout.setObjectName(u"main_pages_layout")
        self.main_pages_layout.setContentsMargins(5, 5, 5, 5)
        self.pages = QStackedWidget(MainPages)
        self.pages.setObjectName(u"pages")
        self.page_1 = QWidget()
        self.page_1.setObjectName(u"page_1")
        self.page_1.setStyleSheet(u"font-size: 14pt")
        self.page_1_layout = QVBoxLayout(self.page_1)
        self.page_1_layout.setSpacing(5)
        self.page_1_layout.setObjectName(u"page_1_layout")
        self.page_1_layout.setContentsMargins(5, 5, 5, 5)
        self.homeTitle = QLabel(self.page_1)
        self.homeTitle.setObjectName(u"homeTitle")
        self.homeTitle.setMaximumSize(QSize(16777215, 50))
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.homeTitle.setFont(font)
        self.homeTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.page_1_layout.addWidget(self.homeTitle)

        self.homeContentLayout = QVBoxLayout()
        self.homeContentLayout.setObjectName(u"homeContentLayout")

        self.page_1_layout.addLayout(self.homeContentLayout)

        self.pages.addWidget(self.page_1)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.page_2.setStyleSheet(u"QFrame { font-size: 16pt;}")
        self.page_2_layout = QVBoxLayout(self.page_2)
        self.page_2_layout.setObjectName(u"page_2_layout")
        self.aiTitle = QLabel(self.page_2)
        self.aiTitle.setObjectName(u"aiTitle")
        self.aiTitle.setMaximumSize(QSize(16777215, 75))
        font1 = QFont()
        font1.setPointSize(16)
        font1.setBold(True)
        self.aiTitle.setFont(font1)
        self.aiTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.page_2_layout.addWidget(self.aiTitle)

        self.aiContentLayout = QVBoxLayout()
        self.aiContentLayout.setObjectName(u"aiContentLayout")

        self.page_2_layout.addLayout(self.aiContentLayout)

        self.pages.addWidget(self.page_2)
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.page_3.setStyleSheet(u"font-size: 16pt")
        self.page_3_layout = QVBoxLayout(self.page_3)
        self.page_3_layout.setSpacing(5)
        self.page_3_layout.setObjectName(u"page_3_layout")
        self.page_3_layout.setContentsMargins(5, 5, 5, 5)
        self.powerTitle = QLabel(self.page_3)
        self.powerTitle.setObjectName(u"powerTitle")
        self.powerTitle.setMaximumSize(QSize(16777215, 50))
        self.powerTitle.setFont(font1)
        self.powerTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.page_3_layout.addWidget(self.powerTitle)

        self.powerContentLayout = QVBoxLayout()
        self.powerContentLayout.setObjectName(u"powerContentLayout")

        self.page_3_layout.addLayout(self.powerContentLayout)

        self.pages.addWidget(self.page_3)
        self.page_4 = QWidget()
        self.page_4.setObjectName(u"page_4")
        self.page_4.setStyleSheet(u"font-size: 16pt")
        self.page_4_layout = QVBoxLayout(self.page_4)
        self.page_4_layout.setSpacing(5)
        self.page_4_layout.setObjectName(u"page_4_layout")
        self.page_4_layout.setContentsMargins(5, 5, 5, 5)
        self.optimizeTitle = QLabel(self.page_4)
        self.optimizeTitle.setObjectName(u"optimizeTitle")
        self.optimizeTitle.setMaximumSize(QSize(16777215, 50))
        self.optimizeTitle.setFont(font1)
        self.optimizeTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.page_4_layout.addWidget(self.optimizeTitle)

        self.topButtonLayout = QHBoxLayout()
        self.topButtonLayout.setObjectName(u"topButtonLayout")

        self.page_4_layout.addLayout(self.topButtonLayout)

        self.frameStackedWidget = QStackedWidget(self.page_4)
        self.frameStackedWidget.setObjectName(u"frameStackedWidget")

        self.page_4_layout.addWidget(self.frameStackedWidget)

        self.pages.addWidget(self.page_4)

        self.main_pages_layout.addWidget(self.pages)


        self.retranslateUi(MainPages)

        self.pages.setCurrentIndex(3)


        QMetaObject.connectSlotsByName(MainPages)
    # setupUi

    def retranslateUi(self, MainPages):
        MainPages.setWindowTitle(QCoreApplication.translate("MainPages", u"Form", None))
        self.homeTitle.setText(QCoreApplication.translate("MainPages", u"Astreis", None))
        self.aiTitle.setText("")
        self.powerTitle.setText("")
        self.optimizeTitle.setText(QCoreApplication.translate("MainPages", u"Advanced Optimization", None))
    # retranslateUi

