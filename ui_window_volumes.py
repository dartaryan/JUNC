# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:/Users/darta/AppData/Local/Temp/window_volumesclxLUu.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Volumes_Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(550, 300)
        Form.setMinimumSize(QtCore.QSize(550, 300))
        Form.setMaximumSize(QtCore.QSize(550, 300))
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.f_table = QtWidgets.QFrame(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.f_table.sizePolicy().hasHeightForWidth())
        self.f_table.setSizePolicy(sizePolicy)
        self.f_table.setStyleSheet("\n"
"QFrame#f_table {\n"
"    background-color: #2C303A;\n"
"    border-radius: 25px;\n"
"}")
        self.f_table.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.f_table.setFrameShadow(QtWidgets.QFrame.Raised)
        self.f_table.setObjectName("f_table")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.f_table)
        self.verticalLayout.setContentsMargins(0, 0, 0, -1)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.f_table_toolbar = QtWidgets.QFrame(self.f_table)
        self.f_table_toolbar.setStyleSheet("QFrame#f_table_toolbar{\n"
"    background-color: rgba(68, 75, 90, 100);\n"
"    border-top-left-radius: 25px;\n"
"    border-top-right-radius: 25px;\n"
"}")
        self.f_table_toolbar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.f_table_toolbar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.f_table_toolbar.setObjectName("f_table_toolbar")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.f_table_toolbar)
        self.horizontalLayout_3.setContentsMargins(10, 7, 10, 3)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.f_toolbar_changes = QtWidgets.QFrame(self.f_table_toolbar)
        self.f_toolbar_changes.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.f_toolbar_changes.setFrameShadow(QtWidgets.QFrame.Raised)
        self.f_toolbar_changes.setObjectName("f_toolbar_changes")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.f_toolbar_changes)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.b_clear_all = QtWidgets.QPushButton(self.f_toolbar_changes)
        self.b_clear_all.setMinimumSize(QtCore.QSize(50, 50))
        self.b_clear_all.setMaximumSize(QtCore.QSize(50, 50))
        font = QtGui.QFont()
        font.setFamily("Icons-JUNC-1")
        font.setPointSize(15)
        self.b_clear_all.setFont(font)
        self.b_clear_all.setStyleSheet("QPushButton{\n"
"    background-color: rgba(0,0,0,0);\n"
"    color: rgb(234, 94, 124);\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"color: rgb(202, 81, 107);\n"
"}\n"
"QPushButton:pressed{\n"
"color: rgb(120, 48, 63);\n"
"}\n"
"")
        self.b_clear_all.setObjectName("b_clear_all")
        self.horizontalLayout_5.addWidget(self.b_clear_all, 0, QtCore.Qt.AlignTop)
        self.horizontalLayout_3.addWidget(self.f_toolbar_changes, 0, QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.f_window_name_volumes = QtWidgets.QFrame(self.f_table_toolbar)
        self.f_window_name_volumes.setStyleSheet("QLabel#window_name_volumes{background-color: rgba(239, 239, 239,50);\n"
"font: 14pt \"Rubik\";\n"
"color: rgb(159, 159, 159);\n"
"border-radius: 7px;}")
        self.f_window_name_volumes.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.f_window_name_volumes.setFrameShadow(QtWidgets.QFrame.Raised)
        self.f_window_name_volumes.setObjectName("f_window_name_volumes")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.f_window_name_volumes)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.window_name_volumes = QtWidgets.QLabel(self.f_window_name_volumes)
        self.window_name_volumes.setStyleSheet("padding:0 5px 0 5px;")
        self.window_name_volumes.setAlignment(QtCore.Qt.AlignCenter)
        self.window_name_volumes.setObjectName("window_name_volumes")
        self.horizontalLayout_2.addWidget(self.window_name_volumes, 0, QtCore.Qt.AlignHCenter)
        self.horizontalLayout_3.addWidget(self.f_window_name_volumes)
        self.f_toolbar_finish = QtWidgets.QFrame(self.f_table_toolbar)
        self.f_toolbar_finish.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.f_toolbar_finish.setFrameShadow(QtWidgets.QFrame.Raised)
        self.f_toolbar_finish.setObjectName("f_toolbar_finish")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.f_toolbar_finish)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.b_accept_table = QtWidgets.QPushButton(self.f_toolbar_finish)
        self.b_accept_table.setMinimumSize(QtCore.QSize(50, 50))
        self.b_accept_table.setMaximumSize(QtCore.QSize(50, 50))
        font = QtGui.QFont()
        font.setFamily("Icons-JUNC-1")
        font.setPointSize(15)
        self.b_accept_table.setFont(font)
        self.b_accept_table.setStyleSheet("QPushButton {\n"
"    background-color: rgba(0,0,0,0);\n"
"    color: rgb(51, 152, 143);\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    color: rgb(37, 113, 105);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    color: rgb(25, 79, 73);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"    color: rgb(138, 134, 121);\n"
"}")
        self.b_accept_table.setObjectName("b_accept_table")
        self.horizontalLayout_6.addWidget(self.b_accept_table)
        self.b_close_table = QtWidgets.QPushButton(self.f_toolbar_finish)
        self.b_close_table.setMinimumSize(QtCore.QSize(50, 50))
        self.b_close_table.setMaximumSize(QtCore.QSize(50, 50))
        font = QtGui.QFont()
        font.setFamily("Icons-JUNC-1")
        font.setPointSize(15)
        self.b_close_table.setFont(font)
        self.b_close_table.setStyleSheet("QPushButton{\n"
"    background-color: rgba(0,0,0,0);\n"
"    color: rgb(182, 75, 77);\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"        color: rgba(165, 0, 41, 200);\n"
"}\n"
"QPushButton:pressed{\n"
"    color: rgba(165, 0, 41, 110);\n"
"}\n"
"")
        self.b_close_table.setObjectName("b_close_table")
        self.horizontalLayout_6.addWidget(self.b_close_table)
        self.horizontalLayout_3.addWidget(self.f_toolbar_finish, 0, QtCore.Qt.AlignRight|QtCore.Qt.AlignTop)
        self.verticalLayout.addWidget(self.f_table_toolbar, 0, QtCore.Qt.AlignTop)
        self.f_table_main = QtWidgets.QFrame(self.f_table)
        self.f_table_main.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.f_table_main.setFrameShadow(QtWidgets.QFrame.Raised)
        self.f_table_main.setObjectName("f_table_main")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.f_table_main)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.f_table_fill = QtWidgets.QFrame(self.f_table_main)
        self.f_table_fill.setStyleSheet("QLineEdit#mor_l,\n"
"#mor_t,\n"
"#mor_r {\n"
"    background-color: rgb(44, 48, 58);\n"
"    font: 14pt \"Rubik\";\n"
"    color: rgb(236, 168, 66);\n"
"    border:none;\n"
"    border-bottom: 2px solid rgb(200, 200, 200);\n"
"}\n"
"\n"
"QLineEdit#eve_l,\n"
"#eve_t,\n"
"#eve_r {\n"
"    background-color: rgb(44, 48, 58);\n"
"    font: 14pt \"Rubik\";\n"
"    color: rgb(157, 207, 221);\n"
"    border:none;\n"
"    border-bottom: 2px solid rgb(200, 200, 200);\n"
"\n"
"}\n"
"\n"
"QLabel#l_fill_l, #l_fill_t, #l_fill_r {\n"
"    background-color: rgba(157, 207, 221,0);\n"
"    color: rgb(255, 255, 255);\n"
"    border-radius: 5px;\n"
"    font: 35pt \"Traffic Arrows\";\n"
"\n"
"}\n"
"\n"
"\n"
"QLabel#l_fill_mor{\n"
"    background-color: rgba(157, 207, 221,0);\n"
"    font:  19pt \"Icons-JUNC-1\";\n"
"    color: rgb(236, 168, 66);\n"
"}\n"
"\n"
"QLabel#l_fill_eve {\n"
"    background-color: rgba(157, 207, 221,0);\n"
"    font:  19pt \"Icons-JUNC-1\";\n"
"    color: rgb(157, 207, 221);\n"
"}\n"
"\n"
"")
        self.f_table_fill.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.f_table_fill.setFrameShadow(QtWidgets.QFrame.Raised)
        self.f_table_fill.setObjectName("f_table_fill")
        self.gridLayout = QtWidgets.QGridLayout(self.f_table_fill)
        self.gridLayout.setHorizontalSpacing(20)
        self.gridLayout.setVerticalSpacing(15)
        self.gridLayout.setObjectName("gridLayout")
        self.l_fill_eve = QtWidgets.QLabel(self.f_table_fill)
        font = QtGui.QFont()
        font.setFamily("Icons-JUNC-1")
        font.setPointSize(19)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.l_fill_eve.setFont(font)
        self.l_fill_eve.setObjectName("l_fill_eve")
        self.gridLayout.addWidget(self.l_fill_eve, 2, 9, 1, 1)
        self.eve_t = QtWidgets.QLineEdit(self.f_table_fill)
        self.eve_t.setClearButtonEnabled(True)
        self.eve_t.setObjectName("eve_t")
        self.gridLayout.addWidget(self.eve_t, 2, 4, 1, 1)
        self.eve_r = QtWidgets.QLineEdit(self.f_table_fill)
        self.eve_r.setClearButtonEnabled(True)
        self.eve_r.setObjectName("eve_r")
        self.gridLayout.addWidget(self.eve_r, 2, 6, 1, 1)
        self.l_fill_mor = QtWidgets.QLabel(self.f_table_fill)
        font = QtGui.QFont()
        font.setFamily("Icons-JUNC-1")
        font.setPointSize(19)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.l_fill_mor.setFont(font)
        self.l_fill_mor.setObjectName("l_fill_mor")
        self.gridLayout.addWidget(self.l_fill_mor, 1, 9, 1, 1)
        self.eve_l = QtWidgets.QLineEdit(self.f_table_fill)
        self.eve_l.setClearButtonEnabled(True)
        self.eve_l.setObjectName("eve_l")
        self.gridLayout.addWidget(self.eve_l, 2, 2, 1, 1)
        self.l_fill_r = QtWidgets.QLabel(self.f_table_fill)
        self.l_fill_r.setObjectName("l_fill_r")
        self.gridLayout.addWidget(self.l_fill_r, 0, 6, 1, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.l_fill_t = QtWidgets.QLabel(self.f_table_fill)
        self.l_fill_t.setObjectName("l_fill_t")
        self.gridLayout.addWidget(self.l_fill_t, 0, 4, 1, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.mor_t = QtWidgets.QLineEdit(self.f_table_fill)
        self.mor_t.setClearButtonEnabled(True)
        self.mor_t.setObjectName("mor_t")
        self.gridLayout.addWidget(self.mor_t, 1, 4, 1, 1)
        self.mor_l = QtWidgets.QLineEdit(self.f_table_fill)
        self.mor_l.setClearButtonEnabled(True)
        self.mor_l.setObjectName("mor_l")
        self.gridLayout.addWidget(self.mor_l, 1, 2, 1, 1)
        self.l_fill_l = QtWidgets.QLabel(self.f_table_fill)
        font = QtGui.QFont()
        font.setFamily("Traffic Arrows")
        font.setPointSize(35)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.l_fill_l.setFont(font)
        self.l_fill_l.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.l_fill_l.setObjectName("l_fill_l")
        self.gridLayout.addWidget(self.l_fill_l, 0, 2, 1, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.mor_r = QtWidgets.QLineEdit(self.f_table_fill)
        self.mor_r.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.mor_r.setDragEnabled(True)
        self.mor_r.setCursorMoveStyle(QtCore.Qt.LogicalMoveStyle)
        self.mor_r.setClearButtonEnabled(True)
        self.mor_r.setObjectName("mor_r")
        self.gridLayout.addWidget(self.mor_r, 1, 6, 1, 1)
        self.horizontalLayout_7.addWidget(self.f_table_fill)
        self.verticalLayout.addWidget(self.f_table_main, 0, QtCore.Qt.AlignTop)
        self.horizontalLayout.addWidget(self.f_table, 0, QtCore.Qt.AlignTop)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.b_clear_all.setText(_translate("Form", "a"))
        self.window_name_volumes.setText(_translate("Form", "-"))
        self.b_accept_table.setText(_translate("Form", "b"))
        self.b_close_table.setText(_translate("Form", "V"))
        self.l_fill_eve.setText(_translate("Form", "d"))
        self.l_fill_mor.setText(_translate("Form", "c"))
        self.l_fill_r.setText(_translate("Form", "r"))
        self.l_fill_t.setText(_translate("Form", "t"))
        self.l_fill_l.setText(_translate("Form", "l"))
import icons_rc
