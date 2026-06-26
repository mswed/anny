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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QDoubleSpinBox,
    QFontComboBox, QGridLayout, QGroupBox, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QSpinBox,
    QToolButton, QVBoxLayout, QWidget)

from text_editor import TextEditWithCommit
import resources_rc

class Ui_Inspector(object):
    def setupUi(self, Inspector):
        if not Inspector.objectName():
            Inspector.setObjectName(u"Inspector")
        Inspector.resize(348, 607)
        self.verticalLayout = QVBoxLayout(Inspector)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.toolsLayout = QGridLayout()
        self.toolsLayout.setObjectName(u"toolsLayout")
        self.freeBtn = QToolButton(Inspector)
        self.freeBtn.setObjectName(u"freeBtn")
        self.freeBtn.setMaximumSize(QSize(28, 28))
        icon = QIcon()
        icon.addFile(u":/icons/pen-solid-full.svg", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        self.freeBtn.setIcon(icon)
        self.freeBtn.setCheckable(True)

        self.toolsLayout.addWidget(self.freeBtn, 0, 2, 1, 1)

        self.lineBtn = QToolButton(Inspector)
        self.lineBtn.setObjectName(u"lineBtn")
        self.lineBtn.setMaximumSize(QSize(28, 28))
        icon1 = QIcon()
        icon1.addFile(u":/icons/slash-solid-full.svg", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        self.lineBtn.setIcon(icon1)
        self.lineBtn.setCheckable(True)

        self.toolsLayout.addWidget(self.lineBtn, 0, 3, 1, 1)

        self.circleBtn = QToolButton(Inspector)
        self.circleBtn.setObjectName(u"circleBtn")
        self.circleBtn.setMaximumSize(QSize(28, 28))
        icon2 = QIcon()
        icon2.addFile(u":/icons/circle-regular-full.svg", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        self.circleBtn.setIcon(icon2)
        self.circleBtn.setCheckable(True)

        self.toolsLayout.addWidget(self.circleBtn, 0, 5, 1, 1)

        self.rectBtn = QToolButton(Inspector)
        self.rectBtn.setObjectName(u"rectBtn")
        self.rectBtn.setMaximumSize(QSize(28, 28))
        icon3 = QIcon()
        icon3.addFile(u":/icons/square-regular-full.svg", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        self.rectBtn.setIcon(icon3)
        self.rectBtn.setCheckable(True)

        self.toolsLayout.addWidget(self.rectBtn, 0, 4, 1, 1)

        self.selectBtn = QToolButton(Inspector)
        self.selectBtn.setObjectName(u"selectBtn")
        self.selectBtn.setMaximumSize(QSize(28, 28))
        icon4 = QIcon()
        icon4.addFile(u":/icons/arrow-pointer-solid-full.svg", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        self.selectBtn.setIcon(icon4)
        self.selectBtn.setCheckable(True)

        self.toolsLayout.addWidget(self.selectBtn, 0, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.toolsLayout.addItem(self.horizontalSpacer, 0, 7, 1, 1)

        self.textBtn = QToolButton(Inspector)
        self.textBtn.setObjectName(u"textBtn")
        self.textBtn.setMaximumSize(QSize(28, 28))
        icon5 = QIcon()
        icon5.addFile(u":/icons/font-solid-full.svg", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        self.textBtn.setIcon(icon5)
        self.textBtn.setCheckable(True)

        self.toolsLayout.addWidget(self.textBtn, 0, 6, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.toolsLayout.addItem(self.horizontalSpacer_2, 0, 0, 1, 1)


        self.mainLayout.addLayout(self.toolsLayout)

        self.strokeBox = QGroupBox(Inspector)
        self.strokeBox.setObjectName(u"strokeBox")
        self.strokeBox.setFlat(False)
        self.gridLayout_4 = QGridLayout(self.strokeBox)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.strokeWidthField = QDoubleSpinBox(self.strokeBox)
        self.strokeWidthField.setObjectName(u"strokeWidthField")
        self.strokeWidthField.setMaximumSize(QSize(60, 16777215))
        self.strokeWidthField.setMinimum(0.100000000000000)
        self.strokeWidthField.setValue(5.000000000000000)

        self.gridLayout_4.addWidget(self.strokeWidthField, 0, 1, 1, 1)

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

        self.endCapLabel = QLabel(self.strokeBox)
        self.endCapLabel.setObjectName(u"endCapLabel")

        self.gridLayout_4.addWidget(self.endCapLabel, 1, 2, 1, 1)

        self.strokeOpacityField = QDoubleSpinBox(self.strokeBox)
        self.strokeOpacityField.setObjectName(u"strokeOpacityField")
        self.strokeOpacityField.setMaximumSize(QSize(60, 16777215))
        self.strokeOpacityField.setMaximum(1.000000000000000)
        self.strokeOpacityField.setSingleStep(0.100000000000000)
        self.strokeOpacityField.setValue(1.000000000000000)

        self.gridLayout_4.addWidget(self.strokeOpacityField, 0, 3, 1, 1)

        self.startCapCb = QComboBox(self.strokeBox)
        self.startCapCb.setObjectName(u"startCapCb")
        self.startCapCb.setMaximumSize(QSize(60, 16777215))

        self.gridLayout_4.addWidget(self.startCapCb, 1, 1, 1, 1)

        self.endCapCb = QComboBox(self.strokeBox)
        self.endCapCb.setObjectName(u"endCapCb")
        self.endCapCb.setMaximumSize(QSize(60, 16777215))

        self.gridLayout_4.addWidget(self.endCapCb, 1, 3, 1, 1)

        self.startCapLabel = QLabel(self.strokeBox)
        self.startCapLabel.setObjectName(u"startCapLabel")

        self.gridLayout_4.addWidget(self.startCapLabel, 1, 0, 1, 1)

        self.strokeOpacityLabel = QLabel(self.strokeBox)
        self.strokeOpacityLabel.setObjectName(u"strokeOpacityLabel")

        self.gridLayout_4.addWidget(self.strokeOpacityLabel, 0, 2, 1, 1)

        self.strokeWidthLabel = QLabel(self.strokeBox)
        self.strokeWidthLabel.setObjectName(u"strokeWidthLabel")

        self.gridLayout_4.addWidget(self.strokeWidthLabel, 0, 0, 1, 1)

        self.smoothingLabel = QLabel(self.strokeBox)
        self.smoothingLabel.setObjectName(u"smoothingLabel")

        self.gridLayout_4.addWidget(self.smoothingLabel, 2, 0, 1, 1)

        self.strokeSmoothingField = QSpinBox(self.strokeBox)
        self.strokeSmoothingField.setObjectName(u"strokeSmoothingField")
        self.strokeSmoothingField.setMaximumSize(QSize(60, 16777215))
        self.strokeSmoothingField.setMaximum(5)

        self.gridLayout_4.addWidget(self.strokeSmoothingField, 2, 1, 1, 1)

        self.gridLayout_4.setColumnStretch(0, 1)

        self.mainLayout.addWidget(self.strokeBox)

        self.fillBox = QGroupBox(Inspector)
        self.fillBox.setObjectName(u"fillBox")
        self.gridLayout = QGridLayout(self.fillBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.fillOpacityLabel = QLabel(self.fillBox)
        self.fillOpacityLabel.setObjectName(u"fillOpacityLabel")

        self.gridLayout.addWidget(self.fillOpacityLabel, 0, 0, 1, 1)

        self.fillOpacityField = QDoubleSpinBox(self.fillBox)
        self.fillOpacityField.setObjectName(u"fillOpacityField")
        self.fillOpacityField.setMaximumSize(QSize(60, 16777215))
        self.fillOpacityField.setMaximum(1.000000000000000)
        self.fillOpacityField.setSingleStep(0.100000000000000)
        self.fillOpacityField.setValue(0.500000000000000)

        self.gridLayout.addWidget(self.fillOpacityField, 0, 1, 1, 1)

        self.fillColorBtn = QPushButton(self.fillBox)
        self.fillColorBtn.setObjectName(u"fillColorBtn")
        sizePolicy.setHeightForWidth(self.fillColorBtn.sizePolicy().hasHeightForWidth())
        self.fillColorBtn.setSizePolicy(sizePolicy)
        self.fillColorBtn.setMaximumSize(QSize(24, 24))
        self.fillColorBtn.setAutoFillBackground(False)
        self.fillColorBtn.setStyleSheet(u"background-color: #000000; border: none;")

        self.gridLayout.addWidget(self.fillColorBtn, 0, 2, 1, 1)


        self.mainLayout.addWidget(self.fillBox)

        self.textBox = QGroupBox(Inspector)
        self.textBox.setObjectName(u"textBox")
        self.gridLayout_2 = QGridLayout(self.textBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.fontCb = QFontComboBox(self.textBox)
        self.fontCb.setObjectName(u"fontCb")
        self.fontCb.setMaximumSize(QSize(130, 16777215))

        self.gridLayout_2.addWidget(self.fontCb, 0, 1, 1, 1)

        self.fontLabel = QLabel(self.textBox)
        self.fontLabel.setObjectName(u"fontLabel")

        self.gridLayout_2.addWidget(self.fontLabel, 0, 0, 1, 1)

        self.fontSizeLabel = QLabel(self.textBox)
        self.fontSizeLabel.setObjectName(u"fontSizeLabel")

        self.gridLayout_2.addWidget(self.fontSizeLabel, 0, 2, 1, 1)

        self.fontSizeField = QSpinBox(self.textBox)
        self.fontSizeField.setObjectName(u"fontSizeField")
        self.fontSizeField.setMaximumSize(QSize(60, 16777215))
        self.fontSizeField.setMinimum(1)
        self.fontSizeField.setValue(14)

        self.gridLayout_2.addWidget(self.fontSizeField, 0, 3, 1, 1)

        self.textField = TextEditWithCommit(self.textBox)
        self.textField.setObjectName(u"textField")
        self.textField.setLineWrapColumnOrWidth(0)

        self.gridLayout_2.addWidget(self.textField, 1, 0, 1, 4)


        self.mainLayout.addWidget(self.textBox)

        self.clearFrameBtn = QPushButton(Inspector)
        self.clearFrameBtn.setObjectName(u"clearFrameBtn")

        self.mainLayout.addWidget(self.clearFrameBtn)


        self.verticalLayout.addLayout(self.mainLayout)


        self.retranslateUi(Inspector)

        QMetaObject.connectSlotsByName(Inspector)
    # setupUi

    def retranslateUi(self, Inspector):
        Inspector.setWindowTitle(QCoreApplication.translate("Inspector", u"Anny", None))
        self.freeBtn.setText(QCoreApplication.translate("Inspector", u"F", None))
        self.lineBtn.setText(QCoreApplication.translate("Inspector", u"L", None))
        self.circleBtn.setText(QCoreApplication.translate("Inspector", u"C", None))
        self.rectBtn.setText(QCoreApplication.translate("Inspector", u"R", None))
        self.selectBtn.setText("")
        self.textBtn.setText(QCoreApplication.translate("Inspector", u"T", None))
        self.strokeBox.setTitle(QCoreApplication.translate("Inspector", u"Stroke", None))
        self.strokeColorBtn.setText("")
        self.endCapLabel.setText(QCoreApplication.translate("Inspector", u"End", None))
#if QT_CONFIG(tooltip)
        self.startCapCb.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.endCapCb.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.startCapLabel.setText(QCoreApplication.translate("Inspector", u"Start", None))
        self.strokeOpacityLabel.setText(QCoreApplication.translate("Inspector", u"Opacity", None))
        self.strokeWidthLabel.setText(QCoreApplication.translate("Inspector", u"Width", None))
        self.smoothingLabel.setText(QCoreApplication.translate("Inspector", u"Smoothing", None))
#if QT_CONFIG(tooltip)
        self.strokeSmoothingField.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.fillBox.setTitle(QCoreApplication.translate("Inspector", u"Fill", None))
        self.fillOpacityLabel.setText(QCoreApplication.translate("Inspector", u"Opacity", None))
        self.fillColorBtn.setText("")
        self.textBox.setTitle(QCoreApplication.translate("Inspector", u"Text", None))
        self.fontLabel.setText(QCoreApplication.translate("Inspector", u"Font", None))
        self.fontSizeLabel.setText(QCoreApplication.translate("Inspector", u"Size", None))
        self.clearFrameBtn.setText(QCoreApplication.translate("Inspector", u"Clear Frame", None))
    # retranslateUi

