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
from PySide6.QtWidgets import (QApplication, QDialog, QDoubleSpinBox, QGridLayout,
    QGroupBox, QLabel, QPushButton, QSizePolicy,
    QSpacerItem, QTextEdit, QToolButton, QVBoxLayout,
    QWidget)

class Ui_Inspector(object):
    def setupUi(self, Inspector):
        if not Inspector.objectName():
            Inspector.setObjectName(u"Inspector")
        Inspector.resize(286, 607)
        self.verticalLayoutWidget = QWidget(Inspector)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(0, 0, 284, 410))
        self.mainLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.toolsLayout = QGridLayout()
        self.toolsLayout.setObjectName(u"toolsLayout")
        self.textBtn = QToolButton(self.verticalLayoutWidget)
        self.textBtn.setObjectName(u"textBtn")
        self.textBtn.setCheckable(True)

        self.toolsLayout.addWidget(self.textBtn, 0, 2, 1, 1)

        self.selectBtn = QToolButton(self.verticalLayoutWidget)
        self.selectBtn.setObjectName(u"selectBtn")
        self.selectBtn.setCheckable(True)

        self.toolsLayout.addWidget(self.selectBtn, 0, 0, 1, 1)

        self.circleBtn = QToolButton(self.verticalLayoutWidget)
        self.circleBtn.setObjectName(u"circleBtn")
        self.circleBtn.setCheckable(True)

        self.toolsLayout.addWidget(self.circleBtn, 0, 3, 1, 1)

        self.lineBtn = QToolButton(self.verticalLayoutWidget)
        self.lineBtn.setObjectName(u"lineBtn")
        self.lineBtn.setCheckable(True)

        self.toolsLayout.addWidget(self.lineBtn, 0, 1, 1, 1)

        self.freeBtn = QToolButton(self.verticalLayoutWidget)
        self.freeBtn.setObjectName(u"freeBtn")
        self.freeBtn.setCheckable(True)

        self.toolsLayout.addWidget(self.freeBtn, 0, 4, 1, 1)

        self.smoothLineBtn = QToolButton(self.verticalLayoutWidget)
        self.smoothLineBtn.setObjectName(u"smoothLineBtn")
        self.smoothLineBtn.setCheckable(True)

        self.toolsLayout.addWidget(self.smoothLineBtn, 0, 5, 1, 1)


        self.mainLayout.addLayout(self.toolsLayout)

        self.strokeBox = QGroupBox(self.verticalLayoutWidget)
        self.strokeBox.setObjectName(u"strokeBox")
        self.strokeBox.setFlat(False)
        self.gridLayout_4 = QGridLayout(self.strokeBox)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.strokeWidthLabel = QLabel(self.strokeBox)
        self.strokeWidthLabel.setObjectName(u"strokeWidthLabel")

        self.gridLayout_4.addWidget(self.strokeWidthLabel, 0, 0, 1, 1)

        self.strokeOpacityField = QDoubleSpinBox(self.strokeBox)
        self.strokeOpacityField.setObjectName(u"strokeOpacityField")
        self.strokeOpacityField.setMaximum(1.000000000000000)
        self.strokeOpacityField.setSingleStep(0.100000000000000)
        self.strokeOpacityField.setValue(1.000000000000000)

        self.gridLayout_4.addWidget(self.strokeOpacityField, 0, 3, 1, 1)

        self.strokeColorBtn = QPushButton(self.strokeBox)
        self.strokeColorBtn.setObjectName(u"strokeColorBtn")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.strokeColorBtn.sizePolicy().hasHeightForWidth())
        self.strokeColorBtn.setSizePolicy(sizePolicy)
        self.strokeColorBtn.setMaximumSize(QSize(24, 24))
        self.strokeColorBtn.setAutoFillBackground(False)
        self.strokeColorBtn.setStyleSheet(u"background-color: red; border: none;")

        self.gridLayout_4.addWidget(self.strokeColorBtn, 0, 4, 1, 1)

        self.strokeWidthField = QDoubleSpinBox(self.strokeBox)
        self.strokeWidthField.setObjectName(u"strokeWidthField")
        self.strokeWidthField.setMinimum(0.100000000000000)
        self.strokeWidthField.setValue(1.000000000000000)

        self.gridLayout_4.addWidget(self.strokeWidthField, 0, 1, 1, 1)

        self.strokeOpacityLabel = QLabel(self.strokeBox)
        self.strokeOpacityLabel.setObjectName(u"strokeOpacityLabel")

        self.gridLayout_4.addWidget(self.strokeOpacityLabel, 0, 2, 1, 1)

        self.gridLayout_4.setColumnStretch(0, 1)

        self.mainLayout.addWidget(self.strokeBox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.mainLayout.addItem(self.verticalSpacer)

        self.textField = QTextEdit(self.verticalLayoutWidget)
        self.textField.setObjectName(u"textField")

        self.mainLayout.addWidget(self.textField)


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
        self.strokeBox.setTitle(QCoreApplication.translate("Inspector", u"Stroke", None))
        self.strokeWidthLabel.setText(QCoreApplication.translate("Inspector", u"width", None))
        self.strokeColorBtn.setText("")
        self.strokeOpacityLabel.setText(QCoreApplication.translate("Inspector", u"Opacity", None))
    # retranslateUi

