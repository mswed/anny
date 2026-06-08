# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'inspector.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
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
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QSizePolicy,
    QSpacerItem, QTextEdit, QToolButton, QVBoxLayout,
    QWidget)

class Ui_Inspector(object):
    def setupUi(self, Inspector):
        if not Inspector.objectName():
            Inspector.setObjectName(u"Inspector")
        Inspector.resize(214, 515)
        self.verticalLayoutWidget = QWidget(Inspector)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(0, 0, 201, 501))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.textBtn = QToolButton(self.verticalLayoutWidget)
        self.textBtn.setObjectName(u"textBtn")

        self.gridLayout.addWidget(self.textBtn, 0, 2, 1, 1)

        self.selectBtn = QToolButton(self.verticalLayoutWidget)
        self.selectBtn.setObjectName(u"selectBtn")

        self.gridLayout.addWidget(self.selectBtn, 0, 0, 1, 1)

        self.circleBtn = QToolButton(self.verticalLayoutWidget)
        self.circleBtn.setObjectName(u"circleBtn")

        self.gridLayout.addWidget(self.circleBtn, 0, 3, 1, 1)

        self.lineBtn = QToolButton(self.verticalLayoutWidget)
        self.lineBtn.setObjectName(u"lineBtn")

        self.gridLayout.addWidget(self.lineBtn, 0, 1, 1, 1)

        self.freeBtn = QToolButton(self.verticalLayoutWidget)
        self.freeBtn.setObjectName(u"freeBtn")

        self.gridLayout.addWidget(self.freeBtn, 0, 4, 1, 1)

        self.smoothLineBtn = QToolButton(self.verticalLayoutWidget)
        self.smoothLineBtn.setObjectName(u"smoothLineBtn")

        self.gridLayout.addWidget(self.smoothLineBtn, 0, 5, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.textField = QTextEdit(self.verticalLayoutWidget)
        self.textField.setObjectName(u"textField")

        self.verticalLayout.addWidget(self.textField)


        self.retranslateUi(Inspector)

        QMetaObject.connectSlotsByName(Inspector)
    # setupUi

    def retranslateUi(self, Inspector):
        Inspector.setWindowTitle(QCoreApplication.translate("Inspector", u"Dialog", None))
        self.textBtn.setText(QCoreApplication.translate("Inspector", u"T", None))
        self.selectBtn.setText(QCoreApplication.translate("Inspector", u"S", None))
        self.circleBtn.setText(QCoreApplication.translate("Inspector", u"C", None))
        self.lineBtn.setText(QCoreApplication.translate("Inspector", u"L", None))
        self.freeBtn.setText(QCoreApplication.translate("Inspector", u"F", None))
        self.smoothLineBtn.setText(QCoreApplication.translate("Inspector", u"A", None))
    # retranslateUi

