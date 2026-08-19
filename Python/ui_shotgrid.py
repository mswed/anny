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
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)

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
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.infoLayout = QGridLayout()
        self.infoLayout.setObjectName(u"infoLayout")
        self.artistNameLabel = QLabel(Shotgrid)
        self.artistNameLabel.setObjectName(u"artistNameLabel")

        self.infoLayout.addWidget(self.artistNameLabel, 2, 1, 1, 1)

        self.versionNameLabel = QLabel(Shotgrid)
        self.versionNameLabel.setObjectName(u"versionNameLabel")
        font = QFont()
        font.setPointSize(12)
        self.versionNameLabel.setFont(font)

        self.infoLayout.addWidget(self.versionNameLabel, 1, 0, 1, 1)

        self.entityNameLabel = QLabel(Shotgrid)
        self.entityNameLabel.setObjectName(u"entityNameLabel")
        font1 = QFont()
        font1.setPointSize(14)
        font1.setBold(True)
        self.entityNameLabel.setFont(font1)

        self.infoLayout.addWidget(self.entityNameLabel, 0, 0, 1, 1)

        self.artistLabel = QLabel(Shotgrid)
        self.artistLabel.setObjectName(u"artistLabel")

        self.infoLayout.addWidget(self.artistLabel, 2, 0, 1, 1)

        self.statusLabel = QLabel(Shotgrid)
        self.statusLabel.setObjectName(u"statusLabel")

        self.infoLayout.addWidget(self.statusLabel, 3, 0, 1, 1)

        self.statusCb = QComboBox(Shotgrid)
        self.statusCb.setObjectName(u"statusCb")

        self.infoLayout.addWidget(self.statusCb, 3, 1, 1, 1)


        self.mainLayout.addLayout(self.infoLayout)

        self.subjectLayout = QHBoxLayout()
        self.subjectLayout.setObjectName(u"subjectLayout")
        self.subjectLabel = QLabel(Shotgrid)
        self.subjectLabel.setObjectName(u"subjectLabel")

        self.subjectLayout.addWidget(self.subjectLabel)

        self.subjectField = QLineEdit(Shotgrid)
        self.subjectField.setObjectName(u"subjectField")

        self.subjectLayout.addWidget(self.subjectField)


        self.mainLayout.addLayout(self.subjectLayout)

        self.textField = TextEditWithCommit(Shotgrid)
        self.textField.setObjectName(u"textField")
        self.textField.setLineWrapColumnOrWidth(0)

        self.mainLayout.addWidget(self.textField)

        self.detailsLayout = QFormLayout()
        self.detailsLayout.setObjectName(u"detailsLayout")
        self.toLabel = QLabel(Shotgrid)
        self.toLabel.setObjectName(u"toLabel")

        self.detailsLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.toLabel)

        self.ccLabel = QLabel(Shotgrid)
        self.ccLabel.setObjectName(u"ccLabel")

        self.detailsLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.ccLabel)

        self.tagsLabel = QLabel(Shotgrid)
        self.tagsLabel.setObjectName(u"tagsLabel")

        self.detailsLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.tagsLabel)

        self.noteTypeLabel = QLabel(Shotgrid)
        self.noteTypeLabel.setObjectName(u"noteTypeLabel")

        self.detailsLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.noteTypeLabel)

        self.noteTypeCb = QComboBox(Shotgrid)
        self.noteTypeCb.setObjectName(u"noteTypeCb")

        self.detailsLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.noteTypeCb)

        self.toMs = MultiSelect(Shotgrid)
        self.toMs.setObjectName(u"toMs")

        self.detailsLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.toMs)

        self.ccMs = MultiSelect(Shotgrid)
        self.ccMs.setObjectName(u"ccMs")

        self.detailsLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.ccMs)

        self.tagsMs = MultiSelect(Shotgrid)
        self.tagsMs.setObjectName(u"tagsMs")

        self.detailsLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.tagsMs)


        self.mainLayout.addLayout(self.detailsLayout)

        self.submitBtn = QPushButton(Shotgrid)
        self.submitBtn.setObjectName(u"submitBtn")

        self.mainLayout.addWidget(self.submitBtn)


        self.verticalLayout.addLayout(self.mainLayout)


        self.retranslateUi(Shotgrid)

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
    # retranslateUi

