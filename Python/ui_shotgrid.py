# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'shotgrid.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QFormLayout,
    QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QStackedWidget, QVBoxLayout,
    QWidget)

from multi_select import MultiSelect
from text_editor import TextEditWithCommit
import resources_rc

class Ui_Shotgrid(object):
    def setupUi(self, Shotgrid):
        if not Shotgrid.objectName():
            Shotgrid.setObjectName(u"Shotgrid")
        Shotgrid.resize(348, 577)
        self.verticalLayout = QVBoxLayout(Shotgrid)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.sgStackedWidget = QStackedWidget(Shotgrid)
        self.sgStackedWidget.setObjectName(u"sgStackedWidget")
        self.versionInfoWidget = QWidget()
        self.versionInfoWidget.setObjectName(u"versionInfoWidget")
        self.widget = QWidget(self.versionInfoWidget)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(0, 0, 330, 524))
        self.versionMainLayout = QVBoxLayout(self.widget)
        self.versionMainLayout.setObjectName(u"versionMainLayout")
        self.versionMainLayout.setContentsMargins(8, 8, 8, 8)
        self.infoLayout = QGridLayout()
        self.infoLayout.setObjectName(u"infoLayout")
        self.artistNameLabel = QLabel(self.widget)
        self.artistNameLabel.setObjectName(u"artistNameLabel")

        self.infoLayout.addWidget(self.artistNameLabel, 2, 1, 1, 1)

        self.versionNameLabel = QLabel(self.widget)
        self.versionNameLabel.setObjectName(u"versionNameLabel")
        font = QFont()
        font.setPointSize(12)
        self.versionNameLabel.setFont(font)

        self.infoLayout.addWidget(self.versionNameLabel, 1, 0, 1, 1)

        self.entityNameLabel = QLabel(self.widget)
        self.entityNameLabel.setObjectName(u"entityNameLabel")
        font1 = QFont()
        font1.setPointSize(14)
        font1.setBold(True)
        self.entityNameLabel.setFont(font1)

        self.infoLayout.addWidget(self.entityNameLabel, 0, 0, 1, 1)

        self.artistLabel = QLabel(self.widget)
        self.artistLabel.setObjectName(u"artistLabel")

        self.infoLayout.addWidget(self.artistLabel, 2, 0, 1, 1)

        self.statusLabel = QLabel(self.widget)
        self.statusLabel.setObjectName(u"statusLabel")

        self.infoLayout.addWidget(self.statusLabel, 3, 0, 1, 1)

        self.statusCb = QComboBox(self.widget)
        self.statusCb.setObjectName(u"statusCb")

        self.infoLayout.addWidget(self.statusCb, 3, 1, 1, 1)


        self.versionMainLayout.addLayout(self.infoLayout)

        self.subjectLayout = QHBoxLayout()
        self.subjectLayout.setObjectName(u"subjectLayout")
        self.subjectLabel = QLabel(self.widget)
        self.subjectLabel.setObjectName(u"subjectLabel")

        self.subjectLayout.addWidget(self.subjectLabel)

        self.subjectField = QLineEdit(self.widget)
        self.subjectField.setObjectName(u"subjectField")

        self.subjectLayout.addWidget(self.subjectField)


        self.versionMainLayout.addLayout(self.subjectLayout)

        self.textField = TextEditWithCommit(self.widget)
        self.textField.setObjectName(u"textField")
        self.textField.setLineWrapColumnOrWidth(0)

        self.versionMainLayout.addWidget(self.textField)

        self.detailsLayout = QFormLayout()
        self.detailsLayout.setObjectName(u"detailsLayout")
        self.toLabel = QLabel(self.widget)
        self.toLabel.setObjectName(u"toLabel")

        self.detailsLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.toLabel)

        self.ccLabel = QLabel(self.widget)
        self.ccLabel.setObjectName(u"ccLabel")

        self.detailsLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.ccLabel)

        self.tagsLabel = QLabel(self.widget)
        self.tagsLabel.setObjectName(u"tagsLabel")

        self.detailsLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.tagsLabel)

        self.noteTypeLabel = QLabel(self.widget)
        self.noteTypeLabel.setObjectName(u"noteTypeLabel")

        self.detailsLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.noteTypeLabel)

        self.noteTypeCb = QComboBox(self.widget)
        self.noteTypeCb.setObjectName(u"noteTypeCb")

        self.detailsLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.noteTypeCb)

        self.toMs = MultiSelect(self.widget)
        self.toMs.setObjectName(u"toMs")

        self.detailsLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.toMs)

        self.ccMs = MultiSelect(self.widget)
        self.ccMs.setObjectName(u"ccMs")

        self.detailsLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.ccMs)

        self.tagsMs = MultiSelect(self.widget)
        self.tagsMs.setObjectName(u"tagsMs")

        self.detailsLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.tagsMs)


        self.versionMainLayout.addLayout(self.detailsLayout)

        self.submitBtn = QPushButton(self.widget)
        self.submitBtn.setObjectName(u"submitBtn")

        self.versionMainLayout.addWidget(self.submitBtn)

        self.sgStackedWidget.addWidget(self.versionInfoWidget)
        self.noSGWidget = QWidget()
        self.noSGWidget.setObjectName(u"noSGWidget")
        self.verticalLayout_3 = QVBoxLayout(self.noSGWidget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.shotgridLabel = QLabel(self.noSGWidget)
        self.shotgridLabel.setObjectName(u"shotgridLabel")
        self.shotgridLabel.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.shotgridLabel)

        self.sgStackedWidget.addWidget(self.noSGWidget)

        self.verticalLayout.addWidget(self.sgStackedWidget)


        self.retranslateUi(Shotgrid)

        self.sgStackedWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(Shotgrid)
    # setupUi

    def retranslateUi(self, Shotgrid):
        Shotgrid.setWindowTitle(QCoreApplication.translate("Shotgrid", u"Anny", None))
        self.artistNameLabel.setText(QCoreApplication.translate("Shotgrid", u"Artist Name", None))
        self.versionNameLabel.setText(QCoreApplication.translate("Shotgrid", u"Version Name", None))
        self.entityNameLabel.setText(QCoreApplication.translate("Shotgrid", u"Shot Name", None))
        self.artistLabel.setText(QCoreApplication.translate("Shotgrid", u"Artist", None))
        self.statusLabel.setText(QCoreApplication.translate("Shotgrid", u"Status", None))
        self.subjectLabel.setText(QCoreApplication.translate("Shotgrid", u"Subject", None))
        self.textField.setPlaceholderText(QCoreApplication.translate("Shotgrid", u"Write your note here", None))
        self.toLabel.setText(QCoreApplication.translate("Shotgrid", u"To:", None))
        self.ccLabel.setText(QCoreApplication.translate("Shotgrid", u"CC:", None))
        self.tagsLabel.setText(QCoreApplication.translate("Shotgrid", u"Tags:", None))
        self.noteTypeLabel.setText(QCoreApplication.translate("Shotgrid", u"Type:", None))
        self.submitBtn.setText(QCoreApplication.translate("Shotgrid", u"Submit", None))
        self.shotgridLabel.setText(QCoreApplication.translate("Shotgrid", u"ShotGrid Data Not Available", None))
    # retranslateUi

