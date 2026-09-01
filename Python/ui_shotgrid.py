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
    QPushButton, QSizePolicy, QSpacerItem, QStackedWidget,
    QVBoxLayout, QWidget)

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
        self.layoutWidget = QWidget(self.versionInfoWidget)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(0, 0, 330, 524))
        self.versionMainLayout = QVBoxLayout(self.layoutWidget)
        self.versionMainLayout.setObjectName(u"versionMainLayout")
        self.versionMainLayout.setContentsMargins(8, 8, 8, 8)
        self.headerLayout = QHBoxLayout()
        self.headerLayout.setObjectName(u"headerLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.headerLayout.addItem(self.horizontalSpacer)

        self.refreshBtn = QPushButton(self.layoutWidget)
        self.refreshBtn.setObjectName(u"refreshBtn")
        icon = QIcon()
        icon.addFile(u":/icons/arrow-rotate-left-solid-full.svg", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        self.refreshBtn.setIcon(icon)

        self.headerLayout.addWidget(self.refreshBtn)


        self.versionMainLayout.addLayout(self.headerLayout)

        self.infoLayout = QGridLayout()
        self.infoLayout.setObjectName(u"infoLayout")
        self.artistNameLabel = QLabel(self.layoutWidget)
        self.artistNameLabel.setObjectName(u"artistNameLabel")

        self.infoLayout.addWidget(self.artistNameLabel, 2, 1, 1, 1)

        self.artistLabel = QLabel(self.layoutWidget)
        self.artistLabel.setObjectName(u"artistLabel")

        self.infoLayout.addWidget(self.artistLabel, 2, 0, 1, 1)

        self.statusLabel = QLabel(self.layoutWidget)
        self.statusLabel.setObjectName(u"statusLabel")

        self.infoLayout.addWidget(self.statusLabel, 3, 0, 1, 1)

        self.statusCb = QComboBox(self.layoutWidget)
        self.statusCb.setObjectName(u"statusCb")

        self.infoLayout.addWidget(self.statusCb, 3, 1, 1, 1)

        self.entityNameLabel = QLabel(self.layoutWidget)
        self.entityNameLabel.setObjectName(u"entityNameLabel")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.entityNameLabel.setFont(font)

        self.infoLayout.addWidget(self.entityNameLabel, 0, 0, 1, 2)

        self.versionNameLabel = QLabel(self.layoutWidget)
        self.versionNameLabel.setObjectName(u"versionNameLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.versionNameLabel.sizePolicy().hasHeightForWidth())
        self.versionNameLabel.setSizePolicy(sizePolicy)
        font1 = QFont()
        font1.setPointSize(12)
        self.versionNameLabel.setFont(font1)

        self.infoLayout.addWidget(self.versionNameLabel, 1, 0, 1, 2)


        self.versionMainLayout.addLayout(self.infoLayout)

        self.subjectLayout = QHBoxLayout()
        self.subjectLayout.setObjectName(u"subjectLayout")
        self.subjectLabel = QLabel(self.layoutWidget)
        self.subjectLabel.setObjectName(u"subjectLabel")

        self.subjectLayout.addWidget(self.subjectLabel)

        self.subjectField = QLineEdit(self.layoutWidget)
        self.subjectField.setObjectName(u"subjectField")

        self.subjectLayout.addWidget(self.subjectField)


        self.versionMainLayout.addLayout(self.subjectLayout)

        self.textField = TextEditWithCommit(self.layoutWidget)
        self.textField.setObjectName(u"textField")
        self.textField.setLineWrapColumnOrWidth(0)

        self.versionMainLayout.addWidget(self.textField)

        self.detailsLayout = QFormLayout()
        self.detailsLayout.setObjectName(u"detailsLayout")
        self.toLabel = QLabel(self.layoutWidget)
        self.toLabel.setObjectName(u"toLabel")

        self.detailsLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.toLabel)

        self.ccLabel = QLabel(self.layoutWidget)
        self.ccLabel.setObjectName(u"ccLabel")

        self.detailsLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.ccLabel)

        self.tagsLabel = QLabel(self.layoutWidget)
        self.tagsLabel.setObjectName(u"tagsLabel")

        self.detailsLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.tagsLabel)

        self.noteTypeLabel = QLabel(self.layoutWidget)
        self.noteTypeLabel.setObjectName(u"noteTypeLabel")

        self.detailsLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.noteTypeLabel)

        self.noteTypeCb = QComboBox(self.layoutWidget)
        self.noteTypeCb.setObjectName(u"noteTypeCb")

        self.detailsLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.noteTypeCb)

        self.toMs = MultiSelect(self.layoutWidget)
        self.toMs.setObjectName(u"toMs")

        self.detailsLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.toMs)

        self.ccMs = MultiSelect(self.layoutWidget)
        self.ccMs.setObjectName(u"ccMs")

        self.detailsLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.ccMs)

        self.tagsMs = MultiSelect(self.layoutWidget)
        self.tagsMs.setObjectName(u"tagsMs")

        self.detailsLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.tagsMs)


        self.versionMainLayout.addLayout(self.detailsLayout)

        self.submitBtn = QPushButton(self.layoutWidget)
        self.submitBtn.setObjectName(u"submitBtn")

        self.versionMainLayout.addWidget(self.submitBtn)

        self.sgStackedWidget.addWidget(self.versionInfoWidget)
        self.noSGWidget = QWidget()
        self.noSGWidget.setObjectName(u"noSGWidget")
        self.verticalLayout_3 = QVBoxLayout(self.noSGWidget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_2)

        self.shotgridLabel = QLabel(self.noSGWidget)
        self.shotgridLabel.setObjectName(u"shotgridLabel")
        self.shotgridLabel.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.shotgridLabel)

        self.retryBtn = QPushButton(self.noSGWidget)
        self.retryBtn.setObjectName(u"retryBtn")
        self.retryBtn.setIcon(icon)

        self.verticalLayout_3.addWidget(self.retryBtn)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.sgStackedWidget.addWidget(self.noSGWidget)

        self.verticalLayout.addWidget(self.sgStackedWidget)


        self.retranslateUi(Shotgrid)

        self.sgStackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Shotgrid)
    # setupUi

    def retranslateUi(self, Shotgrid):
        Shotgrid.setWindowTitle(QCoreApplication.translate("Shotgrid", u"Anny", None))
#if QT_CONFIG(tooltip)
        self.refreshBtn.setToolTip(QCoreApplication.translate("Shotgrid", u"<html><head/><body><p>Refresh SG data, including users/groups and tags</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.refreshBtn.setText("")
        self.artistNameLabel.setText(QCoreApplication.translate("Shotgrid", u"Artist Name", None))
        self.artistLabel.setText(QCoreApplication.translate("Shotgrid", u"Artist", None))
        self.statusLabel.setText(QCoreApplication.translate("Shotgrid", u"Status", None))
        self.entityNameLabel.setText(QCoreApplication.translate("Shotgrid", u"Entity Name", None))
        self.versionNameLabel.setText(QCoreApplication.translate("Shotgrid", u"Version Name", None))
        self.subjectLabel.setText(QCoreApplication.translate("Shotgrid", u"Subject", None))
        self.textField.setPlaceholderText(QCoreApplication.translate("Shotgrid", u"Write your note here", None))
        self.toLabel.setText(QCoreApplication.translate("Shotgrid", u"To:", None))
        self.ccLabel.setText(QCoreApplication.translate("Shotgrid", u"CC:", None))
        self.tagsLabel.setText(QCoreApplication.translate("Shotgrid", u"Tags:", None))
        self.noteTypeLabel.setText(QCoreApplication.translate("Shotgrid", u"Type:", None))
        self.submitBtn.setText(QCoreApplication.translate("Shotgrid", u"Submit", None))
        self.shotgridLabel.setText(QCoreApplication.translate("Shotgrid", u"ShotGrid Data Not Available", None))
        self.retryBtn.setText(QCoreApplication.translate("Shotgrid", u"Try Again", None))
    # retranslateUi

