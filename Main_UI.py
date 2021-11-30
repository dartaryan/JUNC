import ctypes
import os
import sys
import time

from screeninfo import get_monitors
from PyQt5.QtCore import QPropertyAnimation, QRegExp, Qt, QRect, QEasingCurve
from PyQt5.QtGui import QColor, QPainter, QRegExpValidator, QFont, QBrush, QPalette, QGuiApplication, QScreen
from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsDropShadowEffect, QFileDialog, QMessageBox, \
    QDesktopWidget, QCheckBox, QGraphicsBlurEffect
# from pydeck import settings
# from win32api import GetSystemMetrics
from AngledObjects import AngledLabel
from Diagram import Diagram
from JUCSON import Jucson
from VOLCOV import VolCov
from ui_main_withside_nosidebar import *
from ui_window_arrows_with_complex import *
from ui_window_volumes import *
from ui_loading_screen import *
import Main_ID

from threading import Thread


def get_display_name():
    GetUserNameEx = ctypes.windll.secur32.GetUserNameExW
    NameDisplay = 3

    size = ctypes.pointer(ctypes.c_ulong(0))
    GetUserNameEx(NameDisplay, None, size)

    nameBuffer = ctypes.create_unicode_buffer(size.contents.value)
    GetUserNameEx(NameDisplay, nameBuffer, size)
    return nameBuffer.value


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.animation2 = QtCore.QPropertyAnimation(self)
        self.animation = QtCore.QPropertyAnimation(self)
        self.volcov = VolCov()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.ui.shadow = QGraphicsDropShadowEffect(self)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.ui.shadow.setXOffset(0)
        self.ui.shadow.setYOffset(0)
        self.ui.shadow.setColor(QColor(1, 1, 1))
        self.setGraphicsEffect(self.ui.shadow)

        self.ui.b_exit.clicked.connect(lambda: self.closeAllWindows())
        self.ui.body_header.mouseMoveEvent = self.moveWindow
        self.ui.menu_button.clicked.connect(lambda: self.slideRightMenu())

        self.mainDiagram = Diagram()
        self.tempDiagram = Diagram()
        self.jucson = Jucson(self.mainDiagram, "")

        self.loading_screen = LoadingForm()
        self.arrow_north_form = ArrowForm(self.mainDiagram, self.tempDiagram, "NO")
        self.arrow_south_form = ArrowForm(self.mainDiagram, self.tempDiagram, "SO")
        self.arrow_east_form = ArrowForm(self.mainDiagram, self.tempDiagram, "EA")
        self.arrow_west_form = ArrowForm(self.mainDiagram, self.tempDiagram, "WE")

        self.volume_north_form = VolumesForm(self.mainDiagram, self.tempDiagram, "NO")
        self.volume_south_form = VolumesForm(self.mainDiagram, self.tempDiagram, "SO")
        self.volume_east_form = VolumesForm(self.mainDiagram, self.tempDiagram, "EA")
        self.volume_west_form = VolumesForm(self.mainDiagram, self.tempDiagram, "WE")

        self.ui.no_dir.clicked.connect(lambda: self.openNorthArrows(self.arrow_north_form))
        self.ui.ea_dir.clicked.connect(lambda: self.openEastArrows(self.arrow_east_form))
        self.ui.so_dir.clicked.connect(lambda: self.openNorthArrows(self.arrow_south_form))
        self.ui.we_dir.clicked.connect(lambda: self.openEastArrows(self.arrow_west_form))

        self.ui.no_vol.clicked.connect(lambda: self.openNorthVolumes(self.volume_north_form))
        self.ui.ea_vol.clicked.connect(lambda: self.openEastVolumes(self.volume_east_form))
        self.ui.so_vol.clicked.connect(lambda: self.openNorthVolumes(self.volume_south_form))
        self.ui.we_vol.clicked.connect(lambda: self.openEastVolumes(self.volume_west_form))

        self.ui.no_name.textEdited.connect(lambda: self.setStreetNameNO())
        self.ui.so_name.textEdited.connect(lambda: self.setStreetNameSO())
        self.ui.ea_name.textEdited.connect(lambda: self.setStreetNameEA())
        self.ui.we_name.textEdited.connect(lambda: self.setStreetNameWE())

        self.arrow_north_form.ui_form.window_name_arrows.setText("צפון")
        self.arrow_south_form.ui_form.window_name_arrows.setText("דרום")
        self.arrow_east_form.ui_form.window_name_arrows.setText("מזרח")
        self.arrow_west_form.ui_form.window_name_arrows.setText("מערב")
        self.volume_north_form.ui_form.window_name_volumes.setText("צפון")
        self.volume_south_form.ui_form.window_name_volumes.setText("דרום")
        self.volume_east_form.ui_form.window_name_volumes.setText("מזרח")
        self.volume_west_form.ui_form.window_name_volumes.setText("מערב")

        self.ui.b_loadxl.clicked.connect(lambda: self.loadVCFile())
        self.ui.b_loadtxt.clicked.connect(lambda: self.loadJucsonFile())
        self.ui.b_save.clicked.connect(lambda: self.saveJucsonFile())
        self.ui.b_dig_delete_all.clicked.connect(lambda: self.clearMassageBox())
        self.ui.b_new.clicked.connect(lambda: self.createNewMessageBox())

        self.ui.b_open_close_edit.clicked.connect(lambda: self.openCloseEditDiagram())
        self.changes_made = False
        self.firstSize = True
        self.display_monitor = 2
        self.allMonitors = {}
        self.app_height = 2
        self.original_base_width = self.ui.main_body_contents.width()
        self.ui.slide_menu.setMaximumWidth(1)
        self.current_user_name = get_display_name()
        self.count_directions = {"NO": 0, "SO": 0, "EA": 0, "WE": 0}
        self.loading_screen.show()
        self.loading_screen.hide()
        self.ui.b_destfolder.clicked.connect(lambda: self.setOutputDirectory())
        # self.ui.b_run.clicked.connect(lambda: self.run_JUNC())
        self.ui.b_run.clicked.connect(lambda: self.run_thread())

        # Direction animations

        self.anim_no_h = QPropertyAnimation(self.ui.f_dig_no, b"minimumHeight")
        self.anim_so_h = QPropertyAnimation(self.ui.f_dig_so, b"minimumHeight")
        self.anim_ea_h = QPropertyAnimation(self.ui.f_dig_ea, b"minimumHeight")
        self.anim_we_h = QPropertyAnimation(self.ui.f_dig_we, b"minimumHeight")
        self.anim_no_w = QPropertyAnimation(self.ui.f_dig_no, b"minimumWidth")
        self.anim_so_w = QPropertyAnimation(self.ui.f_dig_so, b"minimumWidth")
        self.anim_ea_w = QPropertyAnimation(self.ui.f_dig_ea, b"minimumWidth")
        self.anim_we_w = QPropertyAnimation(self.ui.f_dig_we, b"minimumWidth")



        # fix screen sizing #

        # fix labels:
        self.ui.dig_ea_arrows = AngledLabel("tttttttt", 90)
        self.ui.dig_ea_arrows.setParent(self.ui.f_dig_ea_arrows)
        self.ui.dig_ea_arrows.label.setParent(self.ui.f_dig_ea_arrows)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy2 = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setWidthForHeight(self.ui.dig_ea_arrows.sizePolicy().hasWidthForHeight())
        sizePolicy2.setWidthForHeight(self.ui.dig_ea_arrows.label.sizePolicy().hasWidthForHeight())
        self.ui.dig_ea_arrows.setSizePolicy(sizePolicy)
        self.ui.dig_ea_arrows.label.setSizePolicy(sizePolicy2)
        self.ui.dig_ea_arrows.setText("")
        self.ui.dig_ea_arrows.label.setScaledContents(True)
        self.ui.dig_ea_arrows.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.dig_ea_arrows.label.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.dig_ea_arrows.setObjectName("dig_ea_arrows")
        self.ui.horizontalLayout_32.addWidget(self.ui.dig_ea_arrows)

        self.ui.dig_we_arrows = AngledLabel("tttttttt", 270)
        self.ui.dig_we_arrows.setParent(self.ui.f_dig_we_arrows)
        self.ui.dig_we_arrows.label.setParent(self.ui.f_dig_we_arrows)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy2 = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setWidthForHeight(self.ui.dig_ea_arrows.sizePolicy().hasWidthForHeight())
        sizePolicy2.setWidthForHeight(self.ui.dig_ea_arrows.label.sizePolicy().hasWidthForHeight())
        self.ui.dig_we_arrows.setSizePolicy(sizePolicy)
        self.ui.dig_we_arrows.label.setSizePolicy(sizePolicy2)
        self.ui.dig_we_arrows.setText("")
        self.ui.dig_we_arrows.label.setScaledContents(True)
        self.ui.dig_we_arrows.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.dig_we_arrows.label.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.dig_we_arrows.setObjectName("dig_we_arrows")
        self.ui.horizontalLayout_6.addWidget(self.ui.dig_we_arrows)

        self.ui.dig_no_arrows = AngledLabel("tttttttt", 180)
        self.ui.dig_no_arrows.setParent(self.ui.f_dig_no_arrows)
        self.ui.dig_no_arrows.label.setParent(self.ui.f_dig_no_arrows)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy2 = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.ui.dig_no_arrows.setSizePolicy(sizePolicy)
        self.ui.dig_no_arrows.label.setSizePolicy(sizePolicy2)
        self.ui.dig_no_arrows.setMinimumWidth(0)
        self.ui.dig_no_arrows.setText("")
        self.ui.dig_no_arrows.label.setScaledContents(True)
        self.ui.dig_no_arrows.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.dig_no_arrows.label.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.dig_no_arrows.setObjectName("dig_no_arrows")
        self.ui.horizontalLayout_37.addWidget(self.ui.dig_no_arrows)

        self.ui.dig_so_arrows = AngledLabel("tttttttt", 0)
        self.ui.dig_so_arrows.setParent(self.ui.f_dig_so_arrows)
        self.ui.dig_so_arrows.label.setParent(self.ui.f_dig_so_arrows)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy2 = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.ui.dig_so_arrows.setSizePolicy(sizePolicy)
        self.ui.dig_so_arrows.label.setSizePolicy(sizePolicy2)
        self.ui.dig_so_arrows.setMinimumWidth(0)
        self.ui.dig_so_arrows.setText("")
        self.ui.dig_so_arrows.label.setScaledContents(True)
        self.ui.dig_so_arrows.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.dig_so_arrows.label.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.dig_so_arrows.setObjectName("dig_so_arrows")
        self.ui.horizontalLayout_40.addWidget(self.ui.dig_so_arrows)

        self.ui.slide_menu_container.setFixedWidth(0)
        self.tempAuthor = ""
        self.setMonitorSize()
        self.rotate_pixmap()
        self.ui.b_open_close_edit.checkedState = False
        self.ui.b_open_close_edit.setText("W")
        self.ui.f_edit_control_buttons.setMaximumWidth(0)

        self.show()
        self.rotate_pixmap()

        #  Edit menu info
        self.style_mcu = \
            "QDoubleSpinBox#spin_mcu {font: 13pt 'Rubik';color: rgb(48,54,69);border-radius: " \
            "10px;background-color: rgb(217,217,217);}QDoubleSpinBox#spin_mcu::up-arrow {border-left: " \
            "4px solid none;border-right: 4px solid none;border-bottom: 10px solid rgb(48,54,69);width: " \
            "0px;height: 0px;}QDoubleSpinBox#spin_mcu::up-arrow:hover {border-left: 4px solid " \
            "none;border-right: 4px solid none;border-bottom: 10px solid gray;width: 0px;height: " \
            "0px;}QDoubleSpinBox#spin_mcu::up-button {width: 20px;height: 20px;background-color: rgb(" \
            "200,200,200);border-radius: 5px;}QDoubleSpinBox#spin_mcu::down-arrow {border-left: 4px " \
            "solid none;border-right: 4px solid none;border-top: 10px solid rgb(48,54,69);width: " \
            "0px;height: 0px;}QDoubleSpinBox#spin_mcu::down-arrow:hover {border-left: 4px solid " \
            "none;border-right: 4px solid none;border-top: 10px solid gray;width: 0px;height: " \
            "0px;}QDoubleSpinBox#spin_mcu::down-button {width: 20px;height: 20px;background-color: rgb(" \
            "200,200,200);border-radius: 5px;}QDoubleSpinBox#spin_mcu:disabled {font: 13pt " \
            "'Rubik';color: gray;border-radius: 10px;background-color: rgb(227,227," \
            "227);}QDoubleSpinBox#spin_mcu::up-arrow:disabled {border-left: 4px solid none;border-right: " \
            "4px solid none;border-bottom: 10px solid gray;width: 0px;height: " \
            "0px;}QDoubleSpinBox#spin_mcu::down-arrow:disabled {border-left: 4px solid " \
            "none;border-right: 4px solid none;border-top: 10px solid gray;width: 0px;height: 0px;} "

        self.style_lost_time_spinner = \
            "QSpinBox#spin_lost_time {font: 13pt 'Rubik';color: rgb(48,54," \
            "69);border-radius: " \
            "10px;background-color: rgb(217,217,217);}QSpinBox#spin_lost_time::up-arrow {border-left: " \
            "4px solid none;border-right: 4px solid none;border-bottom: 10px solid rgb(48,54," \
            "69);width: 0px;height: 0px;}QSpinBox#spin_lost_time::up-arrow:hover {border-left: 4px " \
            "solid none;border-right: 4px solid none;border-bottom: 10px solid gray;width: " \
            "0px;height: 0px;}QSpinBox#spin_lost_time::up-button {width: 20px;height: " \
            "20px;background-color: rgb(200,200,200);border-radius: " \
            "5px;}QSpinBox#spin_lost_time::down-arrow {border-left: 4px solid none;border-right: 4px " \
            "solid none;border-top: 10px solid rgb(48,54,69);width: 0px;height: " \
            "0px;}QSpinBox#spin_lost_time::down-arrow:hover {border-left: 4px solid " \
            "none;border-right: 4px solid none;border-top: 10px solid gray;width: 0px;height: " \
            "0px;}QSpinBox#spin_lost_time::down-button {width: 20px;height: 20px;background-color: " \
            "rgb(200,200,200);border-radius: 5px;}QSpinBox#spin_lost_time:disabled {font: 13pt " \
            "'Rubik';color: gray;border-radius: 10px;background-color: rgb(227,227," \
            "227);}QSpinBox#spin_lost_time::up-arrow:disabled {border-left: 4px solid " \
            "none;border-right: 4px solid none;border-bottom: 10px solid gray;width: 0px;height: " \
            "0px;}QSpinBox#spin_lost_time::down-arrow:disabled {border-left: 4px solid " \
            "none;border-right: 4px solid none;border-top: 10px solid gray;width: 0px;height: 0px;} "

        self.phaser_input_list = ['Morning',  # 0
                                  "Morning_Volumes",  # 1
                                  "Regular_Arrows",  # 2
                                  ["Capacity", "NLSL_Allowed", "ELWL_Allowed", "5th_Image", "6th_Image", "Geometry_N_S",
                                   "Geometry_E_W", "LOOP", "LRT_Orig", "LRT_Orig", "INF"],  # 3 --> Get from sidebar
                                  ["rakal_calc", "cycle_time", "train_lost_time", "train_headway", "LRT_MCU",
                                   "GEN_LOST_TIME"],
                                  # 4 --> Get from sidebar
                                  "PublicTransport_Arrows",  # 5
                                  "Morning_VOC",  # 6
                                  "Morning_Total",  # 7
                                  "Morning images and calculated volumes",  # 8
                                  "Morning_LRT",  # 9
                                  'Evening',  # 10
                                  "Evening_Volumes",  # 11
                                  "Regular_Arrows",  # 12
                                  "General info - similar to #3",  # 13
                                  "LRT info - similar to #4",  # 14
                                  "PublicTransport_Arrows",  # 15
                                  "Evening_VOC",  # 16
                                  "Evening_Total",  # 17
                                  "Evening images and calculated volumes",  # 18
                                  "Evening_LRT",  # 19
                                  ['North', 'South', 'East', "West"],  # 20
                                  ["PROJ_NAME", "PROJ_NUM", "AUTHOR", "COUNT", "INFO"]  # 21 --> Get from sidebar
                                  ]

        self.setLostTime()
        self.first_checks_state()
        self.editSize()

    def createSpinnerStyle(self, spinner):
        style_spinner = \
            "QSpinBox#%s {font: 13pt 'Rubik';color: rgb(48,54," \
            "69);border-radius: " \
            "10px;background-color: rgb(217,217,217);}QSpinBox#%s::up-arrow {border-left: " \
            "4px solid none;border-right: 4px solid none;border-bottom: 10px solid rgb(48,54," \
            "69);width: 0px;height: 0px;}QSpinBox#%s::up-arrow:hover {border-left: 4px " \
            "solid none;border-right: 4px solid none;border-bottom: 10px solid gray;width: " \
            "0px;height: 0px;}QSpinBox#%s::up-button {width: 20px;height: " \
            "20px;background-color: rgb(200,200,200);border-radius: " \
            "5px;}QSpinBox#%s::down-arrow {border-left: 4px solid none;border-right: 4px " \
            "solid none;border-top: 10px solid rgb(48,54,69);width: 0px;height: " \
            "0px;}QSpinBox#%s::down-arrow:hover {border-left: 4px solid " \
            "none;border-right: 4px solid none;border-top: 10px solid gray;width: 0px;height: " \
            "0px;}QSpinBox#%s::down-button {width: 20px;height: 20px;background-color: " \
            "rgb(200,200,200);border-radius: 5px;}QSpinBox#%s:disabled {font: 13pt " \
            "'Rubik';color: gray;border-radius: 10px;background-color: rgb(227,227," \
            "227);}QSpinBox#%s::up-arrow:disabled {border-left: 4px solid " \
            "none;border-right: 4px solid none;border-bottom: 10px solid gray;width: 0px;height: " \
            "0px;}QSpinBox#%s::down-arrow:disabled {border-left: 4px solid " \
            "none;border-right: 4px solid none;border-top: 10px solid gray;width: 0px;height: 0px;} " \
            % (spinner, spinner, spinner, spinner, spinner, spinner, spinner, spinner, spinner, spinner)
        return style_spinner

    def first_checks_state(self):
        self.updatePhaserFromUI()
        self.ui.check_lrt_noso.setChecked(False)
        self.enabledLRT()

        # First Page
        self.ui.txt_pro_name.textEdited.connect(lambda: self.setProjectName())
        self.ui.txt_pro_num.textEdited.connect(lambda: self.setProjectNumber())
        self.ui.txt_author.textEdited.connect(lambda: self.setAuthorName())
        self.ui.check_get_username.clicked.connect(lambda: self.checkBoxAuthor())
        self.ui.txt_ver.textEdited.connect(lambda: self.setCount())
        self.ui.txt_info.textEdited.connect(lambda: self.setMoreInfo())

        # Second Page
        self.ui.spin_cap.valueChanged.connect(lambda: self.setCapacity())
        self.ui.check_noso.stateChanged.connect(lambda: self.setNLSL())
        self.ui.check_weea.stateChanged.connect(lambda: self.setELWL())
        self.ui.check_fifth.stateChanged.connect(lambda: self.set5Image())
        self.ui.check_sixth.stateChanged.connect(lambda: self.set6Image())
        self.ui.spin_inf.valueChanged.connect(lambda: self.setInflation())

        # Third Page
        self.ui.check_lrt_noso.stateChanged.connect(lambda: self.setLrtNS())
        self.ui.check_lrt_weea.stateChanged.connect(lambda: self.setLrtEW())
        self.ui.spin_cyc.valueChanged.connect(lambda: self.setCycleTime())
        self.ui.spin_tr_lost_time.valueChanged.connect(lambda: self.setTrainLostTime())
        self.ui.spin_hd.valueChanged.connect(lambda: self.setTrainHeadway())
        self.ui.spin_mcu.valueChanged.connect(lambda: self.setMCU())
        self.ui.spin_lost_time.valueChanged.connect(lambda: self.setSpinLostTime())
        self.ui.check_lost_time.stateChanged.connect(lambda: self.setLostTime())

        self.ui.b_update.clicked.connect(lambda: self.printPhaserList())
        self.ui.b_restart.clicked.connect(lambda: self.setMenuToDefault())

    def getVolFromJucson(self):
        self.jucson.pull_vol()
        self.phaser_input_list[1] = (self.jucson.OUTJUCSON["Morning_Volumes"])
        self.phaser_input_list[11] = (self.jucson.OUTJUCSON["Evening_Volumes"])

    def getArrowsFromJucson(self):
        self.jucson.pull_arr()
        self.phaser_input_list[2] = (self.jucson.OUTJUCSON["Regular_Arrows"])
        self.phaser_input_list[5] = (self.jucson.OUTJUCSON["PublicTransport_Arrows"])

    def getInfoFromJucson(self):
        project_name = "" if str(self.mainDiagram.ID.PROJ_NAME) == "0" else str(self.mainDiagram.ID.PROJ_NAME)
        author = "" if str(self.mainDiagram.ID.AUTHOR) == "0" else str(self.mainDiagram.ID.AUTHOR)
        project_number = "" if str(self.mainDiagram.ID.PROJ_NUM) == "0" else str(self.mainDiagram.ID.PROJ_NUM)
        count = "" if str(self.mainDiagram.ID.COUNT) == "0" else str(self.mainDiagram.ID.COUNT)
        info = "" if str(self.mainDiagram.ID.INFO) == "0" else str(self.mainDiagram.ID.INFO)

        general_lost_time = self.mainDiagram.LRT_INF.GEN_LOST_TIME
        self.ui.txt_pro_name.setText(project_name)
        self.ui.txt_author.setText(author)
        self.ui.txt_pro_num.setText(project_number)
        self.ui.txt_ver.setText(count)
        self.ui.txt_info.setText(info)
        self.ui.spin_cap.setValue(self.mainDiagram.G_INF.CAP)
        self.ui.check_weea.setChecked(self.mainDiagram.G_INF.ELWL)
        self.ui.check_noso.setChecked(self.mainDiagram.G_INF.NLSL)
        self.ui.spin_inf.setValue(self.mainDiagram.G_INF.INF)

        self.ui.check_fifth.setChecked(True if self.mainDiagram.G_INF.IMG5 == 1 else False)
        self.ui.check_sixth.setChecked(True if self.mainDiagram.G_INF.IMG6 == 1 else False)
        self.ui.check_lrt_noso.setChecked(True if int(self.mainDiagram.LRT_INF.LRT_Orig[0]) == 1 else False)
        self.ui.check_lrt_weea.setChecked(True if int(self.mainDiagram.LRT_INF.LRT_Orig[1]) == 1 else False)

        print("self.ui.check_lrt_noso.isChecked: ", self.ui.check_lrt_noso.isChecked())

        self.enabledLRT()
        if self.ui.check_lrt_noso.isChecked() or self.ui.check_lrt_weea.isChecked():
            self.ui.spin_cyc.setValue(self.mainDiagram.LRT_INF.CYC_TIME)
            self.ui.spin_tr_lost_time.setValue(self.mainDiagram.LRT_INF.LRT_LOST_TIME)
            self.ui.spin_hd.setValue(self.mainDiagram.LRT_INF.LRT_HDWAY)
            self.ui.spin_mcu.setValue(self.mainDiagram.LRT_INF.LRT_MCU)
            if general_lost_time == 0:
                self.ui.check_lost_time.setChecked(True)

            else:
                self.ui.check_lost_time.setChecked(False)
                self.ui.spin_lost_time.setValue(general_lost_time)

    def setMenuToDefault(self):
        self.ui.txt_pro_name.setText("")
        self.ui.txt_author.setText("")
        self.ui.txt_pro_num.setText("")
        self.ui.txt_ver.setText("")
        self.ui.txt_info.setText("")
        self.ui.spin_cap.setValue(1800)

        self.ui.spin_inf.setValue(1)
        self.ui.check_fifth.setChecked(False)
        self.ui.check_sixth.setChecked(False)
        self.ui.check_lrt_noso.setChecked(False)
        self.ui.check_lrt_weea.setChecked(False)
        self.ui.spin_cyc.setValue(120)
        self.ui.spin_tr_lost_time.setValue(25)
        self.ui.spin_hd.setValue(5)
        self.ui.spin_mcu.setValue(1)
        self.ui.spin_lost_time.setValue(0)
        self.ui.check_lost_time.setChecked(True)
        self.ui.check_weea.setChecked(False)
        self.ui.check_noso.setChecked(False)
        self.enabledLRT()

    def updatePhaserFromUI(self):
        self.setLrtNS()
        self.setLrtEW()
        self.setCycleTime()
        self.setTrainLostTime()
        self.setTrainHeadway()
        self.setMCU()
        self.setLostTime()
        self.setSpinLostTime()
        self.setCapacity()
        self.setNLSL()
        self.setELWL()
        self.set5Image()
        self.set6Image()
        self.setInflation()
        self.setProjectName()
        self.setProjectNumber()
        self.setAuthorName()
        self.setCount()
        self.setMoreInfo()

    def run_thread(self):

        t1 = Thread(target=self.run_JUNC())
        t1.start()

    def run_JUNC(self):

        self.loading_h = QPropertyAnimation(self.ui.full_body, b"maximumHeight")
        self.loading_w = QPropertyAnimation(self.ui.full_body, b"maximumWidth")
        window_height = self.ui.full_body.height()
        window_width = self.ui.full_body.width()
        new_size = 0
        print(window_height)

        self.group2 = QtCore.QParallelAnimationGroup()
        self.loading_h.setDuration(250)
        self.loading_h.setStartValue(window_height)
        self.loading_h.setEndValue(new_size)
        self.loading_h.setEasingCurve(QEasingCurve.InOutSine)
        self.group2.addAnimation(self.loading_h)
        self.loading_w.setDuration(250)
        self.loading_w.setStartValue(window_width)
        self.loading_w.setEndValue(new_size)
        self.loading_w.setEasingCurve(QEasingCurve.InOutSine)
        self.group2.addAnimation(self.loading_w)
        self.group2.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

        time.sleep(10)
        self.mainDiagram.phsr_lst = self.phaser_input_list
        Main_ID.set_Diagram(self.mainDiagram)
        final_message = Main_ID.main()
        self.jucson.saveJucsonFromDiagram(self.mainDiagram.OUTPUT + "\\×JUNC×")
        # msgBox = QMessageBox()
        # msgBox.setText("final_message")
        # msgBox.exec()
        old_size = 0

        self.group3 = QtCore.QParallelAnimationGroup()
        self.loading_h.setDuration(250)
        self.loading_h.setStartValue(old_size)
        self.loading_h.setEndValue(window_height)
        self.loading_h.setEasingCurve(QEasingCurve.InOutSine)
        self.group3.addAnimation(self.loading_h)
        self.loading_w.setDuration(250)
        self.loading_w.setStartValue(old_size)
        self.loading_w.setEndValue(window_width)
        self.loading_w.setEasingCurve(QEasingCurve.InOutSine)
        self.group3.addAnimation(self.loading_w)
        self.group3.start(QtCore.QAbstractAnimation.DeleteWhenStopped)



    def setLrtNS(self):
        lrt_NS = 1 if self.ui.check_lrt_noso.isChecked() else 0
        self.phaser_input_list[3][8] = lrt_NS
        self.mainDiagram.LRT_INF.LRT_Orig[0] = lrt_NS
        self.enabledLRT()

    def setLrtEW(self):
        lrt_EW = 1 if self.ui.check_lrt_weea.isChecked() else 0
        self.phaser_input_list[3][9] = lrt_EW
        self.mainDiagram.LRT_INF.LRT_Orig[1] = lrt_EW
        self.enabledLRT()

    def enabledLRT(self):
        if self.ui.check_lrt_noso.isChecked() or self.ui.check_lrt_weea.isChecked():
            self.phaser_input_list[4][0] = 1
            self.ui.f_lrt_enable.setEnabled(True)

        else:
            self.phaser_input_list[4][0] = 0
            self.ui.f_lrt_enable.setEnabled(False)

        self.ui.spin_cyc.setStyleSheet(self.createSpinnerStyle("spin_cyc"))
        self.ui.spin_tr_lost_time.setStyleSheet(self.createSpinnerStyle("spin_tr_lost_time"))
        self.ui.spin_hd.setStyleSheet(self.createSpinnerStyle("spin_hd"))
        self.ui.spin_mcu.setStyleSheet(self.style_mcu)

    def setCycleTime(self):
        cycleTime = int(self.ui.spin_cyc.text())
        self.phaser_input_list[4][1] = cycleTime
        self.mainDiagram.LRT_INF.CYC_TIME = cycleTime

    def setTrainLostTime(self):
        lrtLostTime = int(self.ui.spin_tr_lost_time.text())
        self.phaser_input_list[4][2] = lrtLostTime
        self.mainDiagram.LRT_INF.LRT_LOST_TIME = lrtLostTime

    def setTrainHeadway(self):
        trainHeadway = int(self.ui.spin_hd.text())
        self.phaser_input_list[4][3] = trainHeadway
        self.mainDiagram.LRT_INF.LRT_HDWAY = trainHeadway

    def setMCU(self):
        mcu = float(self.ui.spin_mcu.text())
        self.phaser_input_list[4][4] = mcu
        self.mainDiagram.LRT_INF.LRT_MCU = mcu

    def setLostTime(self):
        if self.ui.check_lost_time.isChecked():
            regularLostTime = 0
            self.ui.spin_lost_time.setDisabled(True)
        else:
            self.ui.spin_lost_time.setEnabled(True)
            regularLostTime = int(self.ui.spin_lost_time.text())

        self.phaser_input_list[4][5] = regularLostTime
        self.mainDiagram.LRT_INF.GEN_LOST_TIME = regularLostTime
        self.ui.spin_lost_time.setStyleSheet(self.style_lost_time_spinner)

    def setSpinLostTime(self):
        regularLostTime = int(self.ui.spin_lost_time.text())
        self.phaser_input_list[4][5] = regularLostTime
        self.mainDiagram.LRT_INF.GEN_LOST_TIME = regularLostTime

    def setCapacity(self):
        capacity = int(self.ui.spin_cap.text())
        self.phaser_input_list[3][0] = capacity
        self.mainDiagram.G_INF.CAP = capacity

    def setNLSL(self):
        self.phaser_input_list[3][1] = 1 if self.ui.check_noso.isChecked() else 0
        self.mainDiagram.G_INF.NLSL = self.ui.check_noso.isChecked()

    def setELWL(self):
        self.phaser_input_list[3][2] = 1 if self.ui.check_weea.isChecked() else 0
        self.mainDiagram.G_INF.ELWL = self.ui.check_weea.isChecked()

    def set5Image(self):
        self.phaser_input_list[3][3] = 1 if self.ui.check_fifth.isChecked() else 0
        self.mainDiagram.G_INF.IMG5 = self.ui.check_fifth.isChecked()

    def set6Image(self):
        self.phaser_input_list[3][4] = 1 if self.ui.check_sixth.isChecked() else 0
        self.mainDiagram.G_INF.IMG6 = self.ui.check_sixth.isChecked()

    def setInflation(self):
        inflation = float(self.ui.spin_inf.text())
        self.phaser_input_list[3][10] = inflation
        self.mainDiagram.G_INF.INF = inflation

    def setProjectName(self):
        projectName = self.ui.txt_pro_name.text()
        self.phaser_input_list[21][0] = projectName
        self.mainDiagram.ID.PROJ_NAME = projectName

    def setProjectNumber(self):
        projectNumber = self.ui.txt_pro_num.text()
        self.phaser_input_list[21][1] = projectNumber
        self.mainDiagram.ID.PROJ_NUM = projectNumber

    def checkBoxAuthor(self):
        if self.ui.check_get_username.isChecked():
            author = self.current_user_name
        else:
            author = self.tempAuthor

        self.ui.txt_author.setText(author)
        self.setAuthorName()

    def setAuthorName(self):
        if not self.ui.check_get_username.isChecked():
            self.tempAuthor = self.ui.txt_author.text()
        author = self.ui.txt_author.text()
        self.phaser_input_list[21][2] = author
        self.mainDiagram.ID.AUTHOR = author

    def setCount(self):
        count = self.ui.txt_ver.text()
        self.phaser_input_list[21][3] = count
        self.mainDiagram.ID.COUNT = count

    def setMoreInfo(self):
        moreInfo = self.ui.txt_info.text()
        self.phaser_input_list[21][4] = moreInfo
        self.mainDiagram.ID.INFO = moreInfo

    def printPhaserList(self):
        self.updatePhaserFromUI()
        print(self.phaser_input_list)

    # Global functions

    def closeAllWindows(self):
        button_value = self.saveMessageBox("close")
        if button_value == "cancel":
            return
        else:
            arrows_volumes = [self.volume_north_form, self.volume_east_form, self.volume_south_form,
                              self.volume_west_form,
                              self.arrow_north_form, self.arrow_east_form, self.arrow_south_form, self.arrow_west_form]

            for cur_form in arrows_volumes:
                if cur_form.isVisible():
                    cur_form.close()
            self.close()

    def openCloseEditDiagram(self):
        if not self.ui.b_open_close_edit.checkedState:
            self.ui.b_open_close_edit.checkedState = True
            self.ui.b_open_close_edit.setText("S")
            old_width = 0
            new_width = 100

        else:
            self.ui.b_open_close_edit.checkedState = False
            self.ui.b_open_close_edit.setText("W")
            old_width = 100
            new_width = 0

        self.animation_regular = QPropertyAnimation(self.ui.f_edit_control_buttons, b"maximumWidth")
        self.animation_regular.setDuration(250)
        self.animation_regular.setStartValue(old_width)
        self.animation_regular.setEndValue(new_width)
        self.animation_regular.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation_regular.start()

    def ToggleNO(self):
        if self.mainDiagram.NO.empty_direction() == 1:
            self.ui.no_check.setDisabled(True)
            self.count_directions["N0"] = 1

        else:
            self.ui.no_check.setEnabled(True)
            self.count_directions["N0"] = 0
        return

    def ToggleSO(self):

        if self.mainDiagram.SO.empty_direction() == 1:
            self.ui.so_check.setDisabled(True)
            self.count_directions["S0"] = 1

        else:
            self.ui.so_check.setEnabled(True)
            self.count_directions["S0"] = 0

        return

    def ToggleEA(self):
        if self.mainDiagram.EA.empty_direction() == 1:
            self.ui.ea_check.setDisabled(True)
            self.count_directions["EA"] = 1

        else:
            self.ui.ea_check.setEnabled(True)
            self.count_directions["EA"] = 0

        return

    def ToggleWE(self):

        if self.mainDiagram.WE.empty_direction() == 1:
            self.ui.we_check.setDisabled(True)
            self.count_directions["WE"] = 1

        else:
            self.ui.we_check.setEnabled(True)
            self.count_directions["WE"] = 0

        return

    def ToggleDirections(self):
        self.ToggleNO()
        self.ToggleSO()
        self.ToggleEA()
        self.ToggleWE()
        self.runButtonWarnings()

        toggles = ["no_check", "so_check", "we_check", "ea_check"]
        for toggle in toggles:
            update_diagram = getattr(self.ui, toggle)
            update_diagram.update()
            update_diagram.repaint()
        return

    def runButtonWarnings(self):
        current_size = [self.ui.f_warning.width(), self.ui.f_warning.height()]
        current_size_txt = [self.ui.warning_txt.width(), self.ui.warning_txt.height()]
        icon_style = "QLabel#warning_icon {font: 18pt 'Icons-JUNC-1';background-color: rgba(1, 1, 1,0);color: rgb(55, " \
                     "62, 78);} "
        text_style = "QLabel#warning_txt {background-color: rgba(1, 1, 1,0);color: rgb(55, 62, 78);font: 10pt 'Rubik';}"

        if sum(self.count_directions.values()) < 3:
            self.ui.b_run.setDisabled(True)
            if not self.changes_made or sum(self.count_directions.values()) == 0:
                message = "יש להזין נתונים על מנת להתחיל. ניתן להקליד או לטעון קובץ מוכן."
                design = "QFrame {border-radius: 12px;background-color: rgba(9, 198, 85, 180);}"
                new_size = [243, 94]
                new_size_txt = [200, 84]
            else:
                message = "יש להזין נתונים בזרועות נוספות על מנת להריץ."
                design = "QFrame {border-radius: 12px;background-color: rgba(248, 228, 2, 120);}"
                new_size = [173, 73]
                new_size_txt = [130, 63]
        else:
            self.ui.b_run.setEnabled(True)
            new_size = [0, 0]
            new_size_txt = [0, 0]
            message = ""
            design = self.ui.f_warning.styleSheet()

        self.anim_warnings_h = QPropertyAnimation(self.ui.f_warning, b"maximumHeight")
        self.anim_warnings_w = QPropertyAnimation(self.ui.f_warning, b"minimumWidth")
        self.anim_warnings_txt_h = QPropertyAnimation(self.ui.warning_txt, b"maximumHeight")
        self.anim_warnings_txt_w = QPropertyAnimation(self.ui.warning_txt, b"minimumWidth")

        f_warnings = [[self.anim_warnings_h, current_size[1], new_size[1]],
                      [self.anim_warnings_w, current_size[0], new_size[0]],
                      [self.anim_warnings_txt_h, current_size_txt[1], new_size_txt[1]],
                      [self.anim_warnings_txt_w, current_size_txt[0], new_size_txt[0]]]

        # [animation_object,current_size,new_size]

        self.group2 = QtCore.QParallelAnimationGroup()
        for animation in f_warnings:
            animation[0].setDuration(50)
            animation[0].setStartValue(animation[1])
            animation[0].setEndValue(animation[2])
            animation[0].setEasingCurve(QEasingCurve.InOutSine)
            self.group2.addAnimation(animation[0])
        self.group2.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

        self.ui.warning_icon.setStyleSheet(icon_style)
        self.ui.warning_txt.setStyleSheet(text_style)
        self.ui.f_warning.setStyleSheet(design)
        self.ui.warning_txt.setText(message)
        self.ui.f_warning.update()
        self.ui.f_warning.repaint()
        self.ui.warning_txt.update()
        self.ui.warning_txt.repaint()
        self.ui.warning_icon.update()
        self.ui.warning_icon.repaint()
        self.ui.warning_txt.update()
        self.ui.warning_txt.repaint()

    def getBaseSize(self):
        if self.firstSize:
            self.firstSize = False
            menu_width = 1
        else:
            menu_width = self.ui.slide_menu_container.width()

        base_size = 0.23 if menu_width != 0 else 0.18
        by_width = int(round((self.ui.full_body.width() * base_size)))
        return by_width

    def editDiagramSize(self):
        old_size = self.ui.f_dig_m.width()
        new_size = self.getBaseSize()
        all_animations = []
        f_digs = [[True, self.anim_no_h, self.anim_no_w],
                  [True, self.anim_so_h, self.anim_so_w],
                  [True, self.anim_ea_h, self.anim_ea_w],
                  [True, self.anim_we_h, self.anim_we_w]]
        self.anim_no_h = QPropertyAnimation(self.ui.f_dig_no, b"minimumHeight")
        self.anim_so_h = QPropertyAnimation(self.ui.f_dig_so, b"minimumHeight")
        self.anim_ea_h = QPropertyAnimation(self.ui.f_dig_ea, b"minimumHeight")
        self.anim_we_h = QPropertyAnimation(self.ui.f_dig_we, b"minimumHeight")
        self.anim_no_w = QPropertyAnimation(self.ui.f_dig_no, b"minimumWidth")
        self.anim_so_w = QPropertyAnimation(self.ui.f_dig_so, b"minimumWidth")
        self.anim_ea_w = QPropertyAnimation(self.ui.f_dig_ea, b"minimumWidth")
        self.anim_we_w = QPropertyAnimation(self.ui.f_dig_we, b"minimumWidth")

        for dig_state in f_digs:
            if dig_state[0]:
                all_animations.append(dig_state[1])
                all_animations.append(dig_state[2])

        self.group1 = QtCore.QParallelAnimationGroup()
        for animation in all_animations:
            print(animation, " : ", old_size, new_size)
            animation.setDuration(550)
            animation.setStartValue(old_size)
            animation.setEndValue(new_size)
            animation.setEasingCurve(QEasingCurve.InOutSine)
            self.group1.addAnimation(animation)
        self.group1.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

    def editSize(self):
        current_monitor = QDesktopWidget().screenNumber(self)
        if current_monitor != self.display_monitor:
            self.display_monitor = current_monitor
        screen_size = self.allMonitors[self.display_monitor]
        screen_app_ratio = 0.9
        app_width_height_ratio = 1.28
        self.app_height = int(round(screen_size[0] * screen_app_ratio, 0))
        app_width = int(round(self.app_height * app_width_height_ratio, 0))
        self.setFixedHeight(self.app_height)
        self.setFixedWidth(app_width)
        self.editDiagramSize()

    def setMonitorSize(self):
        for m in get_monitors():
            self.allMonitors[int(not m.is_primary)] = [m.height, m.width]

    def slideRightMenu(self):
        width = self.ui.slide_menu_container.width()

        if width == 0:
            oldWindowWidth = 1244
            newWindowWidth = 1594
            newWidth = 350

            self.ui.menu_button.setText("W")
            self.ui.body_header.setStyleSheet(
                'QFrame#body_header{background-color: rgb(55, 62, 78);border-top-left-radius: 25px;} QToolTip {'
                'background-color: rgba(43, 49, 63,150);font: 11pt "Rubik";color: rgb(238, 238, 238);border-radius: '
                '2px;border-color: 3px solid rgb(238, 238, 238);}')

        else:
            newWidth = 0
            newWindowWidth = 1244
            oldWindowWidth = 1594
            window_size = "S"
            self.ui.menu_button.setText("L")
            self.ui.body_header.setStyleSheet(
                'QFrame#body_header{background-color: rgb(55, 62, 78);border-top-right-radius: '
                '25px;border-top-left-radius: 25px;} QToolTip {background-color: rgba(43, 49, 63,150);font: 11pt '
                '"Rubik";color: rgb(238, 238, 238);border-radius: 2px;border-color: 3px solid rgb(238, 238, 238);}')

        self.animation = QPropertyAnimation(self.ui.slide_menu_container, b"maximumWidth")
        self.animation.setDuration(350)
        self.animation.setStartValue(width)
        self.animation.setEndValue(newWidth)
        self.animation.setEasingCurve(QEasingCurve.InOutCirc)
        self.editDiagramSize()

        self.animation_window = QPropertyAnimation(self, b"maximumWidth")
        self.animation.setDuration(750)
        self.animation_window.setStartValue(oldWindowWidth)
        self.animation_window.setEndValue(newWindowWidth)
        self.animation_window.setEasingCurve(QEasingCurve.InOutCirc)

        self.group = QtCore.QParallelAnimationGroup(self.ui.slide_menu_container)
        self.group.addAnimation(self.animation)
        self.group.addAnimation(self.animation_window)
        self.group.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

    def setStreetNameNO(self):
        self.updateNamesToMainDiagram("no")
        self.arrow_north_form.ui_form.window_name_arrows.setText(self.ui.no_name.text())
        self.arrow_north_form.ui_form.window_name_arrows.update()
        self.arrow_north_form.ui_form.window_name_arrows.repaint()

        self.volume_north_form.ui_form.window_name_volumes.setText(self.ui.no_name.text())
        self.volume_north_form.ui_form.window_name_volumes.update()
        self.volume_north_form.ui_form.window_name_volumes.repaint()

    def setStreetNameSO(self):
        self.updateNamesToMainDiagram("so")
        self.arrow_south_form.ui_form.window_name_arrows.setText(self.ui.so_name.text())
        self.arrow_south_form.ui_form.window_name_arrows.update()
        self.arrow_south_form.ui_form.window_name_arrows.repaint()

        self.volume_south_form.ui_form.window_name_volumes.setText(self.ui.so_name.text())
        self.volume_south_form.ui_form.window_name_volumes.update()
        self.volume_south_form.ui_form.window_name_volumes.repaint()

    def setStreetNameEA(self):
        self.updateNamesToMainDiagram("ea")
        self.arrow_east_form.ui_form.window_name_arrows.setText(self.ui.ea_name.text())
        self.arrow_east_form.ui_form.window_name_arrows.update()
        self.arrow_east_form.ui_form.window_name_arrows.repaint()

        self.volume_east_form.ui_form.window_name_volumes.setText(self.ui.ea_name.text())
        self.volume_east_form.ui_form.window_name_volumes.update()
        self.volume_east_form.ui_form.window_name_volumes.repaint()

    def setStreetNameWE(self):
        self.updateNamesToMainDiagram("we")
        self.arrow_west_form.ui_form.window_name_arrows.setText(self.ui.we_name.text())
        self.arrow_west_form.ui_form.window_name_arrows.update()
        self.arrow_west_form.ui_form.window_name_arrows.repaint()
        self.volume_west_form.ui_form.window_name_volumes.setText(self.ui.we_name.text())
        self.volume_west_form.ui_form.window_name_volumes.update()
        self.volume_west_form.ui_form.window_name_volumes.repaint()

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()

    def moveWindow(self, e):
        if not self.isMaximized():
            if e.buttons() == QtCore.Qt.LeftButton:
                self.move(self.pos() + e.globalPos() - self.clickPosition)
                self.clickPosition = e.globalPos()
                e.accept()

    def volumesToUi(self):
        all_times = ["MOR", "EVE"]
        all_sides = ["L", "T", "R"]
        temp_options = ["", "0", 0]
        direction_list = ["NO", "SO", "EA", "WE"]
        for direction in direction_list:
            for time in all_times:
                for side in all_sides:
                    main_diag_dir = getattr(self.mainDiagram, direction)
                    main_diag_time = getattr(main_diag_dir, time)
                    main_diag_side = getattr(main_diag_time, side)
                    if main_diag_side in temp_options:
                        main_diag_side = "-"

                    create_dir = "dig_" + direction.lower() + "_vol_" + time.lower() + "_" + side.lower()
                    update_diagram = getattr(self.ui, create_dir)
                    update_diagram.setText(str(main_diag_side))

        for direction in direction_list:
            for time in all_times:
                for side in all_sides:
                    create_dir = "dig_" + direction.lower() + "_vol_" + time.lower() + "_" + side.lower()
                    update_diagram = getattr(self.ui, create_dir)
                    update_diagram.update()
                    update_diagram.repaint()

    def streetsToUi(self):
        direction_list = ["NO", "SO", "EA", "WE"]
        temp_options = ["", "0", 0]
        for direction in direction_list:
            main_diag_dir = getattr(self.mainDiagram, direction)
            main_diag_name = getattr(main_diag_dir, "NAME")
            if main_diag_name in temp_options:
                main_diag_name = ""
            create_dir = direction.lower() + "_name"
            update_diagram = getattr(self.ui, create_dir)
            update_diagram.setText(str(main_diag_name))

        for direction in direction_list:
            create_dir = direction.lower() + "_name"
            update_diagram = getattr(self.ui, create_dir)
            update_diagram.update()
            update_diagram.repaint()

    def arrowsToUi(self):
        direction_list = {"NO": "", "SO": "", "EA": "", "WE": ""}
        colorSet = ("white", "#eca842")
        arrowSet = {"L": "l", "RL": "s", "A": "w", "TL": "a", "T": "t", "TR": "d", "R": "r", "SR": "e"}
        complex_dict = {"RL14": ["JK", "10"], "RL12": ["JK", "01"], "TR13": ["UF", "10"], "TR12": ["UF", "01"],
                        "TL14": ["NU", "10"], "TL13": ["NU", "01"], "A12": ["BF", "01"], "A17": ["BF", "10"],
                        "A14": ["NH", "10"],
                        "A15": ["NH", "01"], "A13": ["NUF", "010"], "A16": ["NUF", "101"]}
        specialArrow = ("RL", "A", "TL", "TR")

        for direction in direction_list.keys():
            final_label_list = []
            diag_dir = getattr(self.mainDiagram, direction)
            diag_lan = getattr(diag_dir, "LAN")

            for arrow in arrowSet.keys():
                diag_arr = getattr(diag_lan, arrow)
                temp_arrow = ["", ""]
                complex_nums = arrow + ''.join(str(num) for num in diag_arr)

                if arrow in specialArrow and complex_nums in complex_dict.keys():
                    cur_complex = complex_dict[complex_nums]

                    for arrow_complex, arrow_type in zip(list(cur_complex[0]), list(cur_complex[1])):
                        start_arr_complex = '<font style="letter-spacing: -0.05em; " color=\"'
                        end_arr_complex = '\">' + arrow_complex + '</font>'
                        temp_local_arr = str(start_arr_complex + colorSet[int(arrow_type)] + end_arr_complex)
                        temp_arrow.append(temp_local_arr)
                    temp_arrow.append('<font style="letter-spacing: -0.3em; " color="#20242d">.</font>')
                    final_combined = ''.join(temp_arrow)
                    final_label_list.append(final_combined)

                else:
                    for i, arr in enumerate(diag_arr):
                        start_arr = '<font color=\"'
                        end_arr = '\">' + arrowSet[arrow] + '</font>'
                        temp_local_arr = str(start_arr + colorSet[i] + end_arr) * arr
                        temp_arrow[i] = temp_local_arr
                    final_label_list.append(''.join(temp_arrow))
            rearrange_final = ''.join(final_label_list)
            direction_list[direction] = rearrange_final
        for direction in direction_list.keys():
            create_dir = "dig_" + direction.lower() + "_arrows"
            update_diagram = getattr(self.ui, create_dir)
            update_diagram.setText(direction_list[direction])
            update_diagram.update()
            update_diagram.repaint()

    def updateUiFromMainDiagram(self):
        self.arrowsToUi()
        self.volumesToUi()
        self.streetsToUi()
        self.getInfoFromJucson()
        self.getVolFromJucson()
        self.getArrowsFromJucson()

        arrows = [self.arrow_north_form, self.arrow_east_form, self.arrow_south_form, self.arrow_west_form]
        for cur_form in arrows:
            cur_form.ui_form.edit_arrows.update()
            cur_form.ui_form.edit_arrows.repaint()

        self.ToggleDirections()

    def updateNamesToMainDiagram(self, direction):
        direction_dict = {"no": "צפון", "so": "דרום", "we": "מערב", "ea": "מזרח"}
        cur_diagram_direction = getattr(self.mainDiagram, direction.upper())
        cur_input_direction = getattr(self.ui, direction + "_name")
        if cur_input_direction.text() == "":
            final_text = direction_dict[direction]
        else:
            final_text = cur_input_direction.text()
        setattr(cur_diagram_direction, "NAME", final_text)
        cur_dig_name = getattr(self.ui, "dig_" + direction + "_name")
        cur_dig_name.setText(final_text)
        cur_dig_name.update()
        cur_dig_name.repaint()

    def saveMessageBox(self, save_type):
        if not self.changes_made:
            return
        else:
            save_options = {"new": "לפני יצירת הקובץ החדש?", "close": "לפני היציאה?", "load": "לפני טעינת קובץ חדש?"}
            msgbox = QMessageBox(QMessageBox.Question, "שמירת נתונים",
                                 "האם ברצונך לשמור {}".format(save_options[save_type]))

            msYes = msgbox.addButton(QMessageBox.Yes)
            msNo = msgbox.addButton(QMessageBox.No)
            msCancel = msgbox.addButton(QMessageBox.Cancel)
            msgbox.setDefaultButton(QMessageBox.Yes)
            msYes.setText("כן")
            msNo.setText("לא")
            msCancel.hide()

            reply = msgbox.exec()
            if reply == QMessageBox.Yes:
                onExit = True if save_type == "close" else False
                self.saveJucsonFile(onExit)
                return ""
            elif reply == QMessageBox.No:
                return ""

            elif reply == QMessageBox.Cancel:
                return "cancel"

    def clearMassageBox(self):
        msgbox = QMessageBox(QMessageBox.Warning, "איפוס נתונים",
                             "פעולה זו תמחק את כל הנתונים. האם ברצונך להמשיך?")
        msYes = msgbox.addButton(QMessageBox.Yes)
        msNo = msgbox.addButton(QMessageBox.No)
        msCancel = msgbox.addButton(QMessageBox.Cancel)
        msgbox.setDefaultButton(QMessageBox.Yes)
        msYes.setText("כן")
        msNo.setText("לא")
        msCancel.hide()

        reply = msgbox.exec()

        if reply == QMessageBox.Yes:
            directory = os.getcwd() + r"\clear_dont_delete.json"
            self.jucson.loadJucson(directory)
            self.updateMainDiagramFromJucson()
            self.openCloseEditDiagram()
            return ""
        elif reply == QMessageBox.No:
            self.openCloseEditDiagram()
            return ""

        elif reply == QMessageBox.Cancel:
            self.openCloseEditDiagram()
            return "cancel"

    def createNewMessageBox(self):
        button_value = self.saveMessageBox("new")
        if button_value == "cancel":
            self.openCloseEditDiagram()
            return
        else:
            directory = os.getcwd() + r"\clear_dont_delete.json"
            self.jucson.loadJucson(directory)
            self.updateMainDiagramFromJucson()
            self.openCloseEditDiagram()

    def saveJucsonFile(self, OnExit=False):
        location = str(QFileDialog.getExistingDirectory(self, "בחירת מיקום לשמירת הקובץ"))
        if location == "":
            if not OnExit:
                msgBox = QMessageBox()
                msgBox.setText("יש לבחור מיקום לשמירת הקובץ")
                msgBox.exec()
                return ""
            else:
                return ""
        else:
            self.jucson.saveJucsonFromDiagram(location)

    def getFileDirectory(self, file_type):
        file_types = {"E": "Excel", "J": "JSON"}
        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        file_path = QFileDialog.getOpenFileName(self, 'בחירת קובץ', desktop, file_type)
        file = file_path[0]

        if file == "":
            orig_msg = file_type.split(" ")[0]
            file_msg = file_types[orig_msg[0]]

            msgBox = QMessageBox()
            msgBox.setText("יש לבחור קובץ {} על מנת להמשיך".format(file_msg))

            msgBox.exec()
            return ""
        else:
            return file

    def setOutputDirectory(self):
        location = str(QFileDialog.getExistingDirectory(self, "בחירת מיקום לייצוא הקובץ הסופי"))
        if location == "":
            msgBox = QMessageBox()
            msgBox.setText("יש לבחור מיקום לייצוא הקובץ הסופי")
            msgBox.exec()
            return ""
        else:

            self.mainDiagram.OUTPUT = location.replace("/", "\\")

    def updateMainDiagramFromJucson(self):
        print("updateMainDiagramFromJucson")
        jucson_methods = ["push_id_info", "push_arr", "push_vol", "push_general_info", "push_lrt_info",
                          "push_street_names"]
        for method in jucson_methods:
            print(method)
            cur_method = getattr(self.jucson, method)
            cur_method()

        self.updateUiFromMainDiagram()

    def loadVCFile(self):
        button_value = self.saveMessageBox("load")
        if button_value == "cancel":
            return
        else:
            filetype = "Excel files (*.xls *.xlsx)"
            directory = self.getFileDirectory(filetype)
            if directory == "":
                return
            else:
                self.volcov.VC = directory
                juc = self.volcov.toJSON()
                self.jucson.JUCSON = juc
                print("loadvc1")
                self.updateMainDiagramFromJucson()

    def loadJucsonFile(self):
        button_value = self.saveMessageBox("load")
        if button_value == "cancel":
            return
        else:
            filetype = "JSON files (*.json)"
            directory = self.getFileDirectory(filetype)
            if directory == "":
                return
            else:
                self.jucson.loadJucson(directory)
                self.updateMainDiagramFromJucson()

    def openNorthArrows(self, form):
        if form.isVisible():
            form.activateWindow()
        else:
            form.checkingOptionUpdate()
            form.updateToWindow("NO")
            self.ui.dig_no_arrows.update()
            self.ui.dig_no_arrows.repaint()
            form.show()

    def openEastArrows(self, form):
        if form.isVisible():
            form.activateWindow()
        else:
            form.checkingOptionUpdate()
            form.updateToWindow("EA")
            self.ui.dig_ea_arrows.update()
            self.ui.dig_ea_arrows.repaint()
            form.show()

    def openSouthArrows(self, form):
        if form.isVisible():
            form.activateWindow()
        else:
            form.checkingOptionUpdate()
            form.updateToWindow("SO")
            self.ui.dig_so_arrows.update()
            self.ui.dig_so_arrows.repaint()
            form.show()

    def openWestArrows(self, form):
        if form.isVisible():
            form.activateWindow()
        else:
            form.checkingOptionUpdate()
            form.updateToWindow("WE")
            self.ui.dig_we_arrows.update()
            self.ui.dig_we_arrows.repaint()
            form.show()

    def openNorthVolumes(self, form):

        if form.isVisible():
            form.activateWindow()
        else:
            form.TableUpdateToWindow()
            form.show()

    def openEastVolumes(self, form):

        if form.isVisible():
            form.activateWindow()

        else:
            form.TableUpdateToWindow()
            form.show()

    def openSouthVolumes(self, form):

        if form.isVisible():
            form.activateWindow()
        else:
            form.TableUpdateToWindow()
            form.show()

    def openWestVolumes(self, form):

        if form.isVisible():
            form.activateWindow()
        else:
            form.TableUpdateToWindow()
            form.show()

    def rotate_pixmap(self):
        rotation = 0
        rotation += 90
        transform = QtGui.QTransform().rotate(rotation)
        painter = QPainter()
        painter.begin(self.ui.dig_no_arrows)
        painter.rotate(45)
        painter.end()


class ArrowForm(QtWidgets.QWidget):
    def __init__(self, mainDiagram, tempDiagram, orig_direction):
        QtWidgets.QWidget.__init__(self)

        # different variables for inner purposes
        self.mainDiagram = mainDiagram
        self.tempDiagram = tempDiagram
        self.or_dir = orig_direction

        self.final_complex = {}
        self.final_text = ""
        self.temp_combined_arrow = []

        self.ui_form = Arrow_Ui_Form()
        self.ui_form.setupUi(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.ui_form.shadow = QGraphicsDropShadowEffect(self)
        self.ui_form.shadow.setBlurRadius(10)
        self.ui_form.shadow.setXOffset(0)
        self.ui_form.shadow.setYOffset(0)
        self.ui_form.shadow.setColor(QColor(1, 1, 1))
        self.setGraphicsEffect(self.ui_form.shadow)
        self.ui_form.f_edit_toolbar.mouseMoveEvent = self.moveForm

        self.ui_form.b_close.clicked.connect(lambda: self.closeWindow())
        self.ui_form.b_clear_all.clicked.connect(lambda: self.clearAll(self.or_dir))
        self.ui_form.b_clear_combined.clicked.connect(lambda: self.deleteFinalCombined())

        self.ui_form.b_combine.checkedState = False
        self.ui_form.b_combine.clicked.connect(lambda: self.changeCombinedState())
        self.ui_form.b_accept.clicked.connect(lambda: self.updateToDiagram(self.or_dir))
        self.ui_form.b_combine_accept.clicked.connect(lambda: self.addCombinedToTemp())
        self.ui_form.b_combine_del.clicked.connect(lambda: self.deleteTempCombined())
        self.ui_form.b_clear_combined.hide()
        self.ui_form.f_arrows_combined_buttons.hide()
        self.ui_form.f_combine_adds.setMaximumWidth(0)
        self.ui_form.f_combine.setStyleSheet("QFrame#f_combine {background-color: rgba(34, 117, 138, 0);}")
        self.ui_form.horizontalLayout_4.setSpacing(30)

        # Connecting arrow buttons  ["l", "rl", "lt", "ltr", "r", "sr", "t", "tr"]

        # ##### Regular arrows ##### #
        self.ui_form.sp_l.valueChanged.connect(
            lambda: self.regularUpdateLabel(self.or_dir, self.ui_form.sp_l, self.ui_form.b_edit_l))
        self.ui_form.b_edit_l.clicked.connect(
            lambda: self.changeColor(self.or_dir, self.ui_form.b_edit_l, self.ui_form.sp_l))

        self.ui_form.sp_rl.valueChanged.connect(
            lambda: self.regularUpdateLabel(self.or_dir, self.ui_form.sp_rl, self.ui_form.b_edit_rl))
        self.ui_form.b_edit_rl.clicked.connect(
            lambda: self.changeColor(self.or_dir, self.ui_form.b_edit_rl, self.ui_form.sp_rl))

        self.ui_form.sp_tl.valueChanged.connect(
            lambda: self.regularUpdateLabel(self.or_dir, self.ui_form.sp_tl, self.ui_form.b_edit_tl))
        self.ui_form.b_edit_tl.clicked.connect(
            lambda: self.changeColor(self.or_dir, self.ui_form.b_edit_tl, self.ui_form.sp_tl))

        self.ui_form.sp_a.valueChanged.connect(
            lambda: self.regularUpdateLabel(self.or_dir, self.ui_form.sp_a, self.ui_form.b_edit_a))
        self.ui_form.b_edit_a.clicked.connect(
            lambda: self.changeColor(self.or_dir, self.ui_form.b_edit_a, self.ui_form.sp_a))

        self.ui_form.sp_r.valueChanged.connect(
            lambda: self.regularUpdateLabel(self.or_dir, self.ui_form.sp_r, self.ui_form.b_edit_r))
        self.ui_form.b_edit_r.clicked.connect(
            lambda: self.changeColor(self.or_dir, self.ui_form.b_edit_r, self.ui_form.sp_r))

        self.ui_form.sp_sr.valueChanged.connect(
            lambda: self.regularUpdateLabel(self.or_dir, self.ui_form.sp_sr, self.ui_form.b_edit_sr))
        self.ui_form.b_edit_sr.clicked.connect(
            lambda: self.changeColor(self.or_dir, self.ui_form.b_edit_sr, self.ui_form.sp_sr))

        self.ui_form.sp_t.valueChanged.connect(
            lambda: self.regularUpdateLabel(self.or_dir, self.ui_form.sp_t, self.ui_form.b_edit_t))
        self.ui_form.b_edit_t.clicked.connect(
            lambda: self.changeColor(self.or_dir, self.ui_form.b_edit_t, self.ui_form.sp_t))

        self.ui_form.sp_tr.valueChanged.connect(
            lambda: self.regularUpdateLabel(self.or_dir, self.ui_form.sp_tr, self.ui_form.b_edit_tr))
        self.ui_form.b_edit_tr.clicked.connect(
            lambda: self.changeColor(self.or_dir, self.ui_form.b_edit_tr, self.ui_form.sp_tr))

        # ##### Combined arrows ##### #
        self.ui_form.sp_l_comb.valueChanged.connect(
            lambda: self.keyToComplex(self.ui_form.b_comb_l))
        self.ui_form.b_comb_l.clicked.connect(
            lambda: self.changeColorCombined(self.ui_form.b_comb_l))

        self.ui_form.sp_t_comb.valueChanged.connect(
            lambda: self.keyToComplex(self.ui_form.b_comb_t))
        self.ui_form.b_comb_t.clicked.connect(
            lambda: self.changeColorCombined(self.ui_form.b_comb_t))

        self.ui_form.sp_r_comb.valueChanged.connect(
            lambda: self.keyToComplex(self.ui_form.b_comb_r))
        self.ui_form.b_comb_r.clicked.connect(
            lambda: self.changeColorCombined(self.ui_form.b_comb_r))

    ##################
    # Window functions
    ##################

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()

    def moveForm(self, e):
        if not self.isMaximized():
            if e.buttons() == QtCore.Qt.LeftButton:
                self.move(self.pos() + e.globalPos() - self.clickPosition)
                self.clickPosition = e.globalPos()
                e.accept()

    def closeWindow(self):
        self.updateToWindow(self.or_dir)
        self.updateFinal()
        self.ui_form.edit_arrows.setText(self.final_text)
        self.ui_form.edit_arrows.update()
        self.ui_form.edit_arrows.repaint()
        self.backToMain(self.or_dir)
        self.close()

    def checkingOptionUpdate(self):
        self.updateToWindow(self.or_dir)
        self.updateFinal()
        self.ui_form.edit_arrows.setText(self.final_text)
        self.ui_form.edit_arrows.update()
        self.ui_form.edit_arrows.repaint()
        self.backToMain(self.or_dir)

    ##################################
    # Combined state related functions
    ##################################

    def openCloseCombinedMenu(self, state):
        new_width = 60 if state else 0
        old_width = 0 if state else 69

        self.animation_reg = QPropertyAnimation(self.ui_form.f_combine_adds, b"maximumWidth")
        self.animation_reg.setDuration(250)
        self.animation_reg.setStartValue(old_width)
        self.animation_reg.setEndValue(new_width)
        self.animation_reg.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation_reg.start()

    def changeCombinedState(self):

        all_arrows = ["a", "sr", "rl", "tl", "tr", "l", "r", "t"]

        self.refreshAll()

        if not self.ui_form.b_combine.checkedState:

            self.UpdateKeyToComplex()
            self.ui_form.b_combine.checkedState = True

            self.ui_form.horizontalLayout_4.setSpacing(20)
            self.ui_form.horizontalLayout_4.setAlignment(QtCore.Qt.AlignHCenter)
            self.ui_form.b_close.setDisabled(True)
            self.ui_form.b_accept.setDisabled(True)
            self.ui_form.b_clear_all.setDisabled(True)
            self.updateArrowCombinedPressed()
            self.ui_form.f_arrows_combined_buttons.show()

            self.ui_form.b_combine.setStyleSheet(
                "QPushButton#b_combine{background-color: rgba(0,0,0,0);color: #1eb7b9;}QPushButton#b_combine:hover{"
                "color: rgba(155,168,182,220);}QPushButton#b_combine:pressed{color: rgba(115,128,142,55);}")
            self.openCloseCombinedMenu(True)
            self.ui_form.f_combine.setStyleSheet(
                "QFrame#f_combine {background-color: rgba(34, 117, 138, 30);border-radius: 15px;}")

            for arrow in all_arrows:
                cur_base_frames = getattr(self, "ui_form")
                cur_arr_frames = getattr(cur_base_frames, "f_edit_" + arrow)
                cur_arr_frames.hide()
            comb_old_height = 0
            reg_old_height = 180
            comb_new_height = 130
            reg_new_height = 0
        else:

            for arrow in all_arrows:
                cur_base_frames = getattr(self, "ui_form")
                cur_arr_frames = getattr(cur_base_frames, "f_edit_" + arrow)
                cur_arr_frames.show()
            self.ui_form.horizontalLayout_4.setSpacing(30)
            # self.ui_form.f_combine_adds.hide()
            self.ui_form.f_arrows_combined_buttons.hide()
            self.ui_form.f_combine.setStyleSheet("QFrame#f_combine {background-color: rgba(34, 117, 138, 0);}")
            self.ui_form.b_close.setEnabled(True)
            self.ui_form.b_accept.setEnabled(True)
            self.ui_form.b_clear_all.setEnabled(True)
            self.ui_form.b_combine.checkedState = False
            self.openCloseCombinedMenu(False)
            self.ui_form.b_combine.setStyleSheet("QPushButton{background-color: rgba(0,0,0,0);color: rgb(47, 119, "
                                                 "138);}QPushButton:hover{color: rgb(34, 117, "
                                                 "138);}QPushButton:pressed{color: rgb(24, 74, 87);}")
            comb_old_height = 180
            reg_old_height = 0
            comb_new_height = 0
            reg_new_height = 130

        self.animation_combined = QPropertyAnimation(self.ui_form.f_combined_arrows, b"maximumHeight")
        self.animation_combined.setDuration(250)
        self.animation_combined.setStartValue(comb_old_height)
        self.animation_combined.setEndValue(comb_new_height)
        self.animation_combined.setEasingCurve(QtCore.QEasingCurve.InOutQuart)

        self.animation_regular = QPropertyAnimation(self.ui_form.f_edit_arrows, b"maximumHeight")
        self.animation_regular.setDuration(250)
        self.animation_regular.setStartValue(reg_old_height)
        self.animation_regular.setEndValue(reg_new_height)
        self.animation_regular.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation_regular.start()
        self.animation_combined.start()

    def updateCombinedError(self):
        combined_arrows = ["l", "t", "r"]
        complex_arrow_dict = {"LR": 0, "TR": 1, "LT": 2, "LTR": 3}
        deeper_complex_dict = {0: {"10": ["JK", "10", "RL", [1, 4]], "01": ["JK", "01", "RL", [1, 2]]},
                               1: {"10": ["UF", "10", "TR", [1, 3]], "01": ["UF", "01", "TR", [1, 2]]},
                               2: {"10": ["NU", "10", "TL", [1, 4]], "01": ["NU", "01", "TL", [1, 3]]},
                               3: {"001": ["BF", "01", "A", [1, 2]], "110": ["BF", "10", "A", [1, 7]],
                                   "100": ["NH", "10", "A", [1, 4]], "011": ["NH", "01", "A", [1, 5]],
                                   "010": ["NUF", "010", "A", [1, 3]], "101": ["NUF", "101", "A", [1, 6]]},
                               }
        arrow_string = ""
        type_string = ""
        for arr_direction in combined_arrows:

            cur_base = getattr(self, "ui_form")
            cur_arr = getattr(cur_base, "sp_" + arr_direction + "_comb")
            cur_arr_button = getattr(cur_base, "b_comb_" + arr_direction)
            arrow_type = self.getArrowColor(cur_arr_button)
            if cur_arr.text() == "0":
                self.final_complex[arr_direction.upper()] = 2
            else:
                self.final_complex[arr_direction.upper()] = arrow_type

        for arr in self.final_complex.keys():

            if self.final_complex[arr] != 2:
                arrow_string += arr
                type_string += str(self.final_complex[arr])
        if arrow_string in complex_arrow_dict.keys() and type_string in deeper_complex_dict[
            complex_arrow_dict[arrow_string]].keys():
            self.ui_form.error_combine.hide()
        else:
            self.ui_form.error_combine.show()

    def addCombinedToTemp(self):
        temp_diag_dir = getattr(self.tempDiagram, self.or_dir)
        temp_diag_lan = getattr(temp_diag_dir, "LAN")
        setattr(temp_diag_lan, self.temp_combined_arrow[0], self.temp_combined_arrow[1])
        self.disableComplexArrows()
        self.changeCombinedState()
        self.deleteTempCombined()

    def deleteTempCombined(self):
        combined_arrows = ["l", "t", "r"]
        for arrow in combined_arrows:
            cur_base = getattr(self, "ui_form")
            cur_arr = getattr(cur_base, "sp_" + arrow + "_comb")
            cur_arr.setValue(0)
            cur_arr_button = getattr(cur_base, "b_comb_" + arrow)
            if self.getArrowColor(cur_arr_button) == 1:
                self.changeColorCombined(cur_arr_button)

        self.ui_form.edit_combined_arrows.setText("")
        self.ui_form.edit_combined_arrows.update()
        self.ui_form.edit_combined_arrows.repaint()

    def changeColorCombined(self, arrow):
        colorDict = {
            "public_complex": "QPushButton{background-color: rgba(34, 117, 138, 150);color: rgba(232,166,66,255);border-radius: 15px;}QPushButton:hover{color: rgba(155,168,182,220);}QPushButton:pressed{color: rgba(115,128,142,255);}QPushButton:disabled{background-color: rgba(120, 120, 120, 80);color: rgba(120,120,120,255);}",
            "regular_complex": "QPushButton{background-color: rgba(34, 117, 138, 150);color: rgba(200,200,200,255);border-radius: 15px;}QPushButton:hover{color: rgba(155,168,182,220);}QPushButton:pressed{color: rgba(115,128,142,255);}QPushButton:disabled{background-color: rgba(120, 120, 120, 80);color: rgba(120,120,120,255);}"
        }
        if arrow.styleSheet() == colorDict["public_complex"]:
            arrow.setStyleSheet(colorDict["regular_complex"])
        else:
            arrow.setStyleSheet(colorDict["public_complex"])
        self.updateArrowCombinedPressed()
        self.UpdateKeyToComplex()

    def updateArrowCombinedPressed(self):
        colorSet = ("rgba(250, 250, 250,", "rgba(236, 168, 66,")
        combined_arrows = ["l", "r", "t"]
        for arrow in combined_arrows:
            cur_base = getattr(self, "ui_form")
            cur_arr = getattr(cur_base, "sp_" + arrow + "_comb")
            cur_arr_frame = getattr(cur_base, "f_comb_" + arrow)
            cur_arr_button = getattr(cur_base, "b_comb_" + arrow)
            cur_color = colorSet[self.getArrowColor(cur_arr_button)]

            if cur_arr.text() == "1":
                final_style = "QSpinBox {font: 1pt 'Rubik';color: rgb(48, 54, 69);border-radius: 45px;background-color: rgba(227, 227, 0, 0);width: 0px;height: 75px;}QSpinBox::up-arrow {border-left: 6px solid rgba(227, 227, 0, 0);border-right: 6px solid rgba(227, 227, 0, 0);border-bottom: 12px solid rgba(227, 227, 0, 0);width: 0px;height: 0px;}QSpinBox::up-button {width: 55px;height: 35px;background-color: %s120);border-radius: 5px;}QSpinBox::up-button:hover {width: 55px;height: 35px;background-color: rgb(100, 100, 100);border-radius: 5px;}QSpinBox::up-arrow:pressed {border-left: 6px solid rgba(227, 227, 0, 0);border-right: 6px solid rgba(227, 227, 0, 0);border-bottom: 12px solid rgba(227, 227, 0, 0);}QSpinBox::up-button:pressed {width: 55px;height: 35px;background-color: rgb(70,70,70);border-radius: 5px;}QSpinBox::down-arrow {border-left: 6px solid rgba(227, 227, 0, 0);border-right: 6px solid rgba(227, 227, 0, 0);border-top: 12px solid rgba(227, 227, 0, 0);width: 0px;height: 0px;}QSpinBox::down-button {width: 55px;height: 35px;background-color: rgb(80, 80,80);border-radius: 5px;}QSpinBox::down-button:hover {width: 55px;height: 35px;background-color: rgb(100, 100, 100);border-radius: 5px;}QSpinBox::down-button:pressed {width: 55px;height: 35px;background-color: rgb(60,60,60);border-radius: 5px;}QSpinBox::down-arrow:pressed {border-left: 6px solid rgba(227, 227, 0, 0);border-right: 6px solid rgba(227, 227, 0, 0);border-top: 12px solid rgba(227, 227, 0, 0);width: 0px;height: 0px;}QSpinBox::up-arrow:disabled {border-left: 6px solid rgba(227, 227, 0, 0);border-right: 6px solid rgba(227, 227, 0, 0);border-bottom: 12px solid rgba(227, 227, 0, 0);}QSpinBox::up-button:disabled {width: 55px;height: 35px;background-color: rgb(68,71,78);border-radius: 5px;}QSpinBox::down-arrow:disabled {border-left: 6px solid rgba(227, 227, 0, 0);border-right: 6px solid rgba(227, 227, 0, 0);border-top: 12px solid rgba(227, 227, 0, 0);width: 0px;height: 0px;}QSpinBox::down-button:disabled {width: 55px;height: 35px;background-color: rgb(68,71,78);border-radius: 5px;}" % cur_color
                cur_arr_frame.setStyleSheet(final_style)


            else:
                final_style = "QSpinBox {font: 1pt 'Rubik';color: rgb(48, 54, 69);border-radius: 45px;background-color: rgba(227, 227, 0, 0);width: 0px;height: 75px;}QSpinBox::up-arrow {border-left: 6px solid rgba(227, 227, 0, 0);border-right: 6px solid rgba(227, 227, 0, 0);border-bottom: 12px solid rgba(227, 227, 0, 0);width: 0px;height: 0px;}QSpinBox::down-button {width: 55px;height: 35px;background-color: %s120);border-radius: 5px;}QSpinBox::down-button:hover {width: 55px;height: 35px;background-color: rgb(100, 100, 100);border-radius: 5px;}QSpinBox::up-arrow:pressed {border-left: 6px solid rgba(227, 227, 0, 0);border-right: 6px solid rgba(227, 227, 0, 0);border-bottom: 12px solid rgba(227, 227, 0, 0);}QSpinBox::down-button:pressed {width: 55px;height: 35px;background-color: rgb(70,70,70);border-radius: 5px;}QSpinBox::down-arrow {border-left: 6px solid rgba(227, 227, 0, 0);border-right: 6px solid rgba(227, 227, 0, 0);border-top: 12px solid rgba(227, 227, 0, 0);width: 0px;height: 0px;}QSpinBox::up-button {width: 55px;height: 35px;background-color: rgb(80, 80,80);border-radius: 5px;}QSpinBox::up-button:hover {width: 55px;height: 35px;background-color: rgb(100, 100, 100);border-radius: 5px;}QSpinBox::up-button:pressed {width: 55px;height: 35px;background-color: rgb(60,60,60);border-radius: 5px;}QSpinBox::down-arrow:pressed {border-left: 6px solid rgba(227, 227, 0, 0);border-right: 6px solid rgba(227, 227, 0, 0);border-top: 12px solid rgba(227, 227, 0, 0);width: 0px;height: 0px;}QSpinBox::up-arrow:disabled {border-left: 6px solid rgba(227, 227, 0, 0);border-right: 6px solid rgba(227, 227, 0, 0);border-bottom: 12px solid rgba(227, 227, 0, 0);}QSpinBox::up-button:disabled {width: 55px;height: 35px;background-color: rgb(68,71,78);border-radius: 5px;}QSpinBox::down-arrow:disabled {border-left: 6px solid rgba(227, 227, 0, 0);border-right: 6px solid rgba(227, 227, 0, 0);border-top: 12px solid rgba(227, 227, 0, 0);width: 0px;height: 0px;}QSpinBox::down-button:disabled {width: 55px;height: 35px;background-color: rgb(68,71,78);border-radius: 5px;}" % cur_color
                cur_arr_frame.setStyleSheet(final_style)

            cur_arr_frame.update()
            cur_arr_frame.repaint()
            cur_arr.update()
            cur_arr.repaint()

    def getBasicRelevantCombined(self):

        # fix through arrow conflict with RL combined! #

        final_list_combined = []
        orig_dir = self.or_dir
        diag_dir = getattr(self.tempDiagram, orig_dir)
        diag_lan = getattr(diag_dir, "LAN")
        special_arrows_dict = {"RL": diag_lan.RL, "A": diag_lan.A, "TL": diag_lan.TL, "TR": diag_lan.TR}

        for arrow in special_arrows_dict.keys():
            diag_arr = getattr(diag_lan, arrow)
            sum_arr = sum(diag_arr)
            if sum_arr == 1:
                final_list_combined.append(arrow)

        return final_list_combined

    def getRelevantCombined(self):
        final_list_combined = []
        orig_dir = self.or_dir
        diag_dir = getattr(self.tempDiagram, orig_dir)
        diag_lan = getattr(diag_dir, "LAN")
        special_arrows_dict = {"RL": diag_lan.RL, "A": diag_lan.A, "TL": diag_lan.TL, "TR": diag_lan.TR}
        complex_list = ['RL14', 'RL12', 'TR13', 'TR12', 'TL14', 'TL13', 'A12', 'A17', 'A14', 'A15', 'A13', 'A16']

        for arrow in special_arrows_dict.keys():
            diag_arr = getattr(diag_lan, arrow)
            sum_arr = sum(diag_arr)

            complex_nums = arrow + ''.join(str(num) for num in diag_arr)
            if complex_nums in complex_list:
                final_list_combined.append(arrow)
        self.showHideClearAllCombined(final_list_combined)
        return final_list_combined

    def disableConflictCombined(self):
        original_relevant_combined = self.getRelevantCombined()
        original_relevant_combined += self.getBasicRelevantCombined()
        replace = ['A']
        relevant_combined = replace if original_relevant_combined == ['TL', 'TR'] else original_relevant_combined
        combined_arrows = ["l", "t", "r"]
        special_arrows_dict = {"RL": ["l", "t", "r"], "A": ["l", "t", "r"], "TL": ["l"], "TR": ["r"]}
        if not original_relevant_combined:
            for arrow in combined_arrows:
                cur_base = getattr(self, "ui_form")
                cur_arr = getattr(cur_base, "sp_" + arrow + "_comb")
                cur_arr_button = getattr(cur_base, "b_comb_" + arrow)
                cur_arr.setEnabled(True)
                cur_arr_button.setEnabled(True)

        for combined in relevant_combined:
            temp_combined = special_arrows_dict[combined]
            for arrow in combined_arrows:
                cur_base = getattr(self, "ui_form")
                cur_arr = getattr(cur_base, "sp_" + arrow + "_comb")
                cur_arr_button = getattr(cur_base, "b_comb_" + arrow)
                if arrow in temp_combined:
                    cur_arr.setDisabled(True)
                    cur_arr_button.setDisabled(True)
                else:
                    cur_arr.setEnabled(True)
                    cur_arr_button.setEnabled(True)

    def showHideClearAllCombined(self, relevant_combined_list):
        if not relevant_combined_list:
            self.ui_form.b_clear_combined.hide()
        else:
            self.ui_form.b_clear_combined.show()

    def disableComplexArrows(self):
        relevant_combined = self.getRelevantCombined()
        orig_dir = self.or_dir
        diag_dir = getattr(self.tempDiagram, orig_dir)
        diag_lan = getattr(diag_dir, "LAN")
        special_arrows_dict = {"RL": diag_lan.RL, "A": diag_lan.A, "TL": diag_lan.TL, "TR": diag_lan.TR}
        iteration_check = {"rl": 0, "a": 0, "tl": 0, "tr": 0, "t": 0}
        arrowSet = {"RL": ["a", "tr", "tl", "t", "rl"], "A": ["tr", "tl", "rl", "t", "a"], "TL": ["a", "rl", "tl"],
                    "TR": ["a", "rl", "tr"]}

        for arrow in arrowSet.keys():
            if arrow in relevant_combined:
                all_arrows = arrowSet[arrow]
                for arrows in all_arrows:
                    if iteration_check[arrows] == 1:
                        continue
                    else:
                        cur_base = getattr(self, "ui_form")
                        cur_arr = getattr(cur_base, "sp_" + arrows)
                        curr_button = getattr(cur_base, "b_edit_" + arrows)
                        cur_arr.setDisabled(True)
                        curr_button.setDisabled(True)
                        iteration_check[arrows] = 1

            elif sum(special_arrows_dict[arrow]) > 0:

                all_arrows = arrowSet[arrow][:-1]
                for arrows in all_arrows:
                    if iteration_check[arrows] == 1:
                        continue
                    else:
                        cur_base = getattr(self, "ui_form")
                        cur_arr = getattr(cur_base, "sp_" + arrows)
                        curr_button = getattr(cur_base, "b_edit_" + arrows)
                        cur_arr.setDisabled(True)
                        curr_button.setDisabled(True)
                        iteration_check[arrows] = 1

            elif sum(special_arrows_dict[arrow]) == 0:
                all_arrows = arrowSet[arrow]
                for arrows in all_arrows:
                    if iteration_check[arrows] == 1:

                        continue
                    else:
                        cur_base = getattr(self, "ui_form")
                        cur_arr = getattr(cur_base, "sp_" + arrows)
                        curr_button = getattr(cur_base, "b_edit_" + arrows)
                        cur_arr.setEnabled(True)
                        curr_button.setEnabled(True)
        full_arrows = ["tr", "tl", "rl", "t", "a"]
        for arrows in full_arrows:
            cur_base = getattr(self, "ui_form")
            cur_arr = getattr(cur_base, "sp_" + arrows)
            curr_button = getattr(cur_base, "b_edit_" + arrows)
            cur_arr.update()
            curr_button.update()
            cur_arr.repaint()
            curr_button.repaint()
        self.updateFinal()

    def deleteFinalCombined(self):
        relevant_combined = self.getRelevantCombined()
        orig_dir = self.or_dir
        diag_dir = getattr(self.tempDiagram, orig_dir)
        diag_lan = getattr(diag_dir, "LAN")

        for arrow in relevant_combined:
            clean_complex = [0, 0]
            setattr(diag_lan, arrow, clean_complex)

        self.disableComplexArrows()
        self.updateFinal()
        self.disableConflictCombined()

    ###################
    # Clear and refresh
    ###################

    def clearLabel(self, orig_dir):
        arrowSet = {"L": "l", "RL": "s", "A": "w", "TL": "a", "T": "t", "TR": "d", "R": "r", "SR": "e"}
        diag_dir = getattr(self.tempDiagram, orig_dir)
        diag_lan = getattr(diag_dir, "LAN")
        for arrow in arrowSet.keys():
            clean_arrow = [0, 0]
            setattr(diag_lan, arrow, clean_arrow)

    def clearAll(self, orig_dir):
        self.deleteFinalCombined()
        if self.ui_form.b_combine.checkedState:
            self.changeCombinedState()

        regular = "QPushButton{background-color: rgb(55, 62, 78);color: rgba(200,200,200,255);border-radius: 15px;}QPushButton:hover{color: rgba(155,168,182,220);}QPushButton:pressed{color: rgba(115,128,142,255);}QPushButton:disabled{color: rgb(120,120,120);}"
        all_arrows = ["l", "rl", "tl", "a", "r", "sr", "t", "tr"]
        for arrow in all_arrows:
            cur_base = getattr(self, "ui_form")
            cur_arr = getattr(cur_base, "sp_" + arrow)
            cur_arr.setValue(0)
            cur_base_button = getattr(self, "ui_form")
            cur_arr_button = getattr(cur_base_button, "b_edit_" + arrow)
            cur_arr_button.setStyleSheet(regular)
        self.clearLabel(orig_dir)
        self.ui_form.edit_arrows.setText("")

    def passIt(self):
        pass

    def refreshAll(self):
        regular = "QPushButton{background-color: rgb(55, 62, 78);color: rgba(200,200,200,255);border-radius: 15px;}QPushButton:hover{color: rgba(155,168,182,220);}QPushButton:pressed{color: rgba(115,128,142,255);}QPushButton:disabled{color: rgb(120,120,120);}"
        all_arrows = ["l", "rl", "tl", "a", "r", "sr", "t", "tr"]
        for arrow in all_arrows:
            cur_base = getattr(self, "ui_form")
            cur_arr = getattr(cur_base, "sp_" + arrow)
            # # cur_arr.valueChanged.connect(lambda: self.passIt())
            # cur_arr.setValue(0)
            cur_base_button = getattr(self, "ui_form")
            cur_arr_button = getattr(cur_base_button, "b_edit_" + arrow)
            cur_arr_button.setStyleSheet(regular)

    ##########################
    # Updates between Diagrams
    ##########################

    def updateToDiagram(self, orig_dir):
        all_arrows = ["L", "RL", "TL", "A", "R", "SR", "T", "TR"]
        window.changes_made = True
        for arrow in all_arrows:
            curr_arr = [0, 0]
            temp_diag_dir = getattr(self.tempDiagram, orig_dir)
            temp_diag_lan = getattr(temp_diag_dir, "LAN")
            temp_diag_arr = getattr(temp_diag_lan, arrow)

            curr_arr[0] = temp_diag_arr[0]
            curr_arr[1] = temp_diag_arr[1]
            main_diag_dir = getattr(self.mainDiagram, orig_dir)
            main_diag_lan = getattr(main_diag_dir, "LAN")
            setattr(main_diag_lan, arrow, curr_arr)

        create_dir = "dig_" + orig_dir.lower() + "_arrows"
        update_ui = getattr(window, "ui")
        update_diagram = getattr(update_ui, create_dir)
        update_diagram.setText(self.ui_form.edit_arrows.text())
        update_diagram.update()
        update_diagram.repaint()
        window.ToggleDirections()
        self.close()

    def updateToWindow(self, orig_dir):
        all_arrows = ["L", "RL", "TL", "A", "R", "SR", "T", "TR"]
        for arrow in all_arrows:
            curr_arr = [0, 0]
            main_diag_dir = getattr(self.mainDiagram, orig_dir)
            main_diag_lan = getattr(main_diag_dir, "LAN")
            main_diag_arr = getattr(main_diag_lan, arrow)

            curr_arr[0] = main_diag_arr[0]
            curr_arr[1] = main_diag_arr[1]
            temp_diag_dir = getattr(self.tempDiagram, orig_dir)
            temp_diag_lan = getattr(temp_diag_dir, "LAN")
            setattr(temp_diag_lan, arrow, curr_arr)

    def backToMain(self, orig_dir):
        all_arrows = ["l", "rl", "tl", "a", "r", "sr", "t", "tr"]
        regular = "QPushButton{background-color: rgb(55, 62, 78);color: rgba(200,200,200,255);border-radius: " \
                  "15px;}QPushButton:hover{color: rgba(155,168,182,220);}QPushButton:pressed{color: rgba(115,128,142," \
                  "255);}QPushButton:disabled{color: rgb(120,120,120);} "
        for arrow in all_arrows:
            main_diag_dir = getattr(self.mainDiagram, orig_dir)
            main_diag_lan = getattr(main_diag_dir, "LAN")
            main_diag_arr = getattr(main_diag_lan, arrow.upper())
            cur_base = getattr(self, "ui_form")
            cur_arr = getattr(cur_base, "sp_" + arrow)
            cur_arr.valueChanged.connect(lambda: self.passIt())
            cur_base_button = getattr(self, "ui_form")
            cur_arr_button = getattr(cur_base_button, "b_edit_" + arrow)
            cur_arr_button.setStyleSheet(regular)
            update_value = main_diag_arr[0]
            cur_arr.setValue(update_value)
            cur_arr.update()
            cur_arr.repaint()

    #########################
    # Arrow control functions
    #########################

    def changeColor(self, orig_dir, arrow, sp_arrow):
        arr_direction = arrow.objectName().split("_")[-1].upper()

        diag_dir = getattr(self.tempDiagram, orig_dir)
        diag_lan = getattr(diag_dir, "LAN")

        side_count_arrow = getattr(diag_lan, arr_direction)

        colorDict = {
            "public": "QPushButton{background-color: rgb(55, 62, 78);color: rgba(232,166,66,255);border-radius: 15px;}QPushButton:hover{color: rgba(155,168,182,220);}QPushButton:pressed{color: rgba(115,128,142,255);}QPushButton:disabled{color: rgb(120,120,120);}",
            "regular": "QPushButton{background-color: rgb(55, 62, 78);color: rgba(200,200,200,255);border-radius: 15px;}QPushButton:hover{color: rgba(155,168,182,220);}QPushButton:pressed{color: rgba(115,128,142,255);}QPushButton:disabled{color: rgb(120,120,120);}"
        }
        temp_counter = int(sp_arrow.text())

        if arrow.styleSheet() == colorDict["public"]:
            arrow.setStyleSheet(colorDict["regular"])
            side_count_arrow[1] = temp_counter
            setattr(diag_lan, arr_direction, side_count_arrow)
            sp_arrow.setValue(side_count_arrow[0])

        else:
            arrow.setStyleSheet(colorDict["public"])
            side_count_arrow[0] = temp_counter
            setattr(diag_lan, arr_direction, side_count_arrow)
            sp_arrow.setValue(side_count_arrow[1])

        self.updateFinal()

    def getArrowColor(self, arrow):
        public = "QPushButton{background-color: rgb(55, 62, 78);color: rgba(232,166,66,255);border-radius: 15px;}QPushButton:hover{color: rgba(155,168,182,220);}QPushButton:pressed{color: rgba(115,128,142,255);}QPushButton:disabled{color: rgb(120,120,120);}"
        regular = "QPushButton{background-color: rgb(55, 62, 78);color: rgba(200,200,200,255);border-radius: 15px;}QPushButton:hover{color: rgba(155,168,182,220);}QPushButton:pressed{color: rgba(115,128,142,255);}QPushButton:disabled{color: rgb(120,120,120);}"
        color_public = "color: rgba(232,166,66,255)"
        color_regular = "color: rgba(200,200,200,255)"

        if arrow.styleSheet() == public or color_public in arrow.styleSheet():
            return 1
        if arrow.styleSheet() == regular or color_regular in arrow.styleSheet():
            return 0

    def keyToComplex(self, b_direction):
        self.updateArrowCombinedPressed()
        self.disableConflictCombined()
        colorSet = ("white", "#eca842")
        complex_arrow_dict = {"LR": 0, "TR": 1, "LT": 2, "LTR": 3}
        deeper_complex_dict = {0: {"10": ["JK", "10", "RL", [1, 4]], "01": ["JK", "01", "RL", [1, 2]]},
                               1: {"10": ["UF", "10", "TR", [1, 3]], "01": ["UF", "01", "TR", [1, 2]]},
                               2: {"10": ["NU", "10", "TL", [1, 4]], "01": ["NU", "01", "TL", [1, 3]]},
                               3: {"001": ["BF", "01", "A", [1, 2]], "110": ["BF", "10", "A", [1, 7]],
                                   "100": ["NH", "10", "A", [1, 4]], "011": ["NH", "01", "A", [1, 5]],
                                   "010": ["NUF", "010", "A", [1, 3]], "101": ["NUF", "101", "A", [1, 6]]},
                               }
        arr_direction = b_direction.objectName().split("_")[-1].upper()
        cur_base = getattr(self, "ui_form")
        cur_arr = getattr(cur_base, "sp_" + arr_direction.lower() + "_comb")
        arrow_type = self.getArrowColor(b_direction)
        if cur_arr.text() == "0":
            self.final_complex[arr_direction] = 2
        else:
            self.final_complex[arr_direction] = arrow_type
        arrow_string = ""
        type_string = ""
        for arr in self.final_complex.keys():
            if self.final_complex[arr] != 2:
                arrow_string += arr
                type_string += str(self.final_complex[arr])

        if arrow_string in complex_arrow_dict.keys() and type_string in deeper_complex_dict[
            complex_arrow_dict[arrow_string]].keys():
            self.ui_form.error_combine.hide()
            self.ui_form.b_combine_accept.setEnabled(True)
            combined_full_info = deeper_complex_dict[complex_arrow_dict[arrow_string]][type_string]

            # ["NUF", "010", "A", [1, 3]]
            temp_arrow = []
            self.temp_combined_arrow = [combined_full_info[2], combined_full_info[3]]

            for arrow, arrow_type in zip(list(combined_full_info[0]), list(combined_full_info[1])):
                start_arr_complex = '<font style="letter-spacing: -0.05em; " color=\"'
                end_arr_complex = '\">' + arrow + '</font>'
                temp_local_arr = str(start_arr_complex + colorSet[int(arrow_type)] + end_arr_complex)
                temp_arrow.append(temp_local_arr)
            final_combined = ''.join(temp_arrow)
            self.ui_form.edit_combined_arrows.setText(final_combined)
            self.ui_form.edit_combined_arrows.update()
            self.ui_form.edit_combined_arrows.repaint()
        else:
            if arrow_string == "":
                self.ui_form.error_combine.hide()
            else:
                self.ui_form.error_combine.show()
            self.ui_form.b_combine_accept.setDisabled(True)
            arrow_list = list(arrow_string)
            temp_arrow = []
            for arrow in arrow_list:
                start_arr_complex = '<font style="letter-spacing: -0.05em; " color=\"'
                end_arr_complex = '\">' + arrow + '</font>'
                temp_local_arr = str(start_arr_complex + "#acacac" + end_arr_complex)
                temp_arrow.append(temp_local_arr)
            final_combined = ''.join(temp_arrow)
            self.ui_form.edit_combined_arrows.setText(final_combined)
            self.ui_form.edit_combined_arrows.update()
            self.ui_form.edit_combined_arrows.repaint()

    def UpdateKeyToComplex(self):

        self.updateArrowCombinedPressed()

        self.disableConflictCombined()

        colorSet = ("white", "#eca842")
        combined_arrows = ["l", "t", "r"]
        complex_arrow_dict = {"LR": 0, "TR": 1, "LT": 2, "LTR": 3}
        deeper_complex_dict = {0: {"10": ["JK", "10", "RL", [1, 4]], "01": ["JK", "01", "RL", [1, 2]]},
                               1: {"10": ["UF", "10", "TR", [1, 3]], "01": ["UF", "01", "TR", [1, 2]]},
                               2: {"10": ["NU", "10", "TL", [1, 4]], "01": ["NU", "01", "TL", [1, 3]]},
                               3: {"001": ["BF", "01", "A", [1, 2]], "110": ["BF", "10", "A", [1, 7]],
                                   "100": ["NH", "10", "A", [1, 4]], "011": ["NH", "01", "A", [1, 5]],
                                   "010": ["NUF", "010", "A", [1, 3]], "101": ["NUF", "101", "A", [1, 6]]},
                               }
        # until here
        arrow_string = ""
        type_string = ""

        for arr_direction in combined_arrows:

            cur_base = getattr(self, "ui_form")
            cur_arr = getattr(cur_base, "sp_" + arr_direction + "_comb")
            cur_arr_button = getattr(cur_base, "b_comb_" + arr_direction)
            arrow_type = self.getArrowColor(cur_arr_button)

            if cur_arr.text() == "0":
                self.final_complex[arr_direction.upper()] = 2
            else:
                self.final_complex[arr_direction.upper()] = arrow_type

        for arr in self.final_complex.keys():

            if self.final_complex[arr] != 2:
                arrow_string += arr
                type_string += str(self.final_complex[arr])

        if arrow_string in complex_arrow_dict.keys() and type_string in deeper_complex_dict[
            complex_arrow_dict[arrow_string]].keys():
            self.ui_form.error_combine.hide()
            self.ui_form.b_combine_accept.setEnabled(True)
            combined_full_info = deeper_complex_dict[complex_arrow_dict[arrow_string]][type_string]
            # ["NUF", "010", "A", [1, 3]]
            temp_arrow = []
            self.temp_combined_arrow = [combined_full_info[2], combined_full_info[3]]

            for arrow, arrow_type in zip(list(combined_full_info[0]), list(combined_full_info[1])):
                start_arr_complex = '<font style="letter-spacing: -0.05em; " color=\"'
                end_arr_complex = '\">' + arrow + '</font>'
                temp_local_arr = str(start_arr_complex + colorSet[int(arrow_type)] + end_arr_complex)
                temp_arrow.append(temp_local_arr)
            final_combined = ''.join(temp_arrow)
            self.ui_form.edit_combined_arrows.setText(final_combined)
            self.ui_form.edit_combined_arrows.update()
            self.ui_form.edit_combined_arrows.repaint()

        else:
            if arrow_string == "":
                self.ui_form.error_combine.hide()
            self.ui_form.b_combine_accept.setDisabled(True)

            arrow_list = list(arrow_string)
            temp_arrow = []
            for arrow in arrow_list:
                start_arr_complex = '<font style="letter-spacing: -0.05em; " color=\"'
                end_arr_complex = '\">' + arrow + '</font>'
                temp_local_arr = str(start_arr_complex + "#acacac" + end_arr_complex)
                temp_arrow.append(temp_local_arr)
            final_combined = ''.join(temp_arrow)
            self.ui_form.edit_combined_arrows.setText(final_combined)
            self.ui_form.edit_combined_arrows.update()
            self.ui_form.edit_combined_arrows.repaint()

    #################
    # Label functions
    #################

    def regularUpdateLabel(self, orig_dir, sp_arrow, b_direction):
        diag_dir = getattr(self.tempDiagram, orig_dir)
        diag_lan = getattr(diag_dir, "LAN")
        arr_direction = b_direction.objectName().split("_")[-1].upper()
        arrow_type = self.getArrowColor(b_direction)
        side_count_arrow = getattr(diag_lan, arr_direction)
        side_count_arrow[arrow_type] = int(sp_arrow.text())
        setattr(diag_lan, arr_direction, side_count_arrow)
        self.disableComplexArrows()

    def updateFinal(self):
        orig_dir = self.or_dir

        final_label_list = []
        colorSet = ("white", "#eca842")
        arrowSet = {"L": "l", "RL": "s", "A": "w", "TL": "a", "T": "t", "TR": "d", "R": "r", "SR": "e"}
        arrowSetComplex = {"L": "J", "RL": "s", "A": "w", "TL": "B", "T": "U", "TR": "d", "R": "K", "SR": "e"}
        complex_dict = {"RL14": ["JK", "10"], "RL12": ["JK", "01"], "TR13": ["UF", "10"], "TR12": ["UF", "01"],
                        "TL14": ["NU", "10"], "TL13": ["NU", "01"], "A12": ["BF", "01"], "A17": ["BF", "10"],
                        "A14": ["NH", "10"],
                        "A15": ["NH", "01"], "A13": ["NUF", "010"], "A16": ["NUF", "101"]}
        specialArrow = ("RL", "A", "TL", "TR")
        diag_dir = getattr(self.tempDiagram, orig_dir)
        diag_lan = getattr(diag_dir, "LAN")
        for arrow in arrowSet.keys():
            diag_arr = getattr(diag_lan, arrow)
            temp_arrow = ["", ""]
            complex_nums = arrow + ''.join(str(num) for num in diag_arr)
            if arrow in specialArrow and complex_nums in complex_dict.keys():
                cur_complex = complex_dict[complex_nums]
                for arrow_complex, arrow_type in zip(list(cur_complex[0]), list(cur_complex[1])):
                    start_arr_complex = '<font style="letter-spacing: -0.05em; " color=\"'
                    end_arr_complex = '\">' + arrow_complex + '</font>'
                    temp_local_arr = str(start_arr_complex + colorSet[int(arrow_type)] + end_arr_complex)

                    temp_arrow.append(temp_local_arr)
                temp_arrow.append('<font style="letter-spacing: -0.3em; " color="#20242d">.</font>')
                final_combined = ''.join(temp_arrow)
                final_label_list.append(final_combined)

            else:
                for i, arr in enumerate(diag_arr):
                    start_arr_complex = '<font style="letter-spacing: -0.2em; " color=\"'
                    start_arr = '<font color=\"'
                    end_arr_complex = '\">' + arrowSetComplex[arrow] + '</font>'
                    end_arr = '\">' + arrowSet[arrow] + '</font>'
                    temp_local_arr = str(start_arr + colorSet[i] + end_arr) * arr
                    temp_arrow[i] = temp_local_arr
                final_label_list.append(''.join(temp_arrow))
        rearrange_final = ''.join(final_label_list)

        self.ui_form.edit_arrows.setText(rearrange_final)
        self.final_text = rearrange_final

    def printDiagrams(self):
        orig_dir = self.or_dir
        all_arrows = ["L", "RL", "TL", "A", "R", "SR", "T", "TR"]

        print("\nMAIN_DIAGRAM")
        for arrow in all_arrows:
            main_diag_dir = getattr(self.mainDiagram, orig_dir)
            main_diag_lan = getattr(main_diag_dir, "LAN")
            main_diag_arr = getattr(main_diag_lan, arrow)
            print(arrow, " : ", main_diag_arr)

        print("\nTEMP_DIAGRAM")
        for arrow in all_arrows:
            temp_diag_dir = getattr(self.tempDiagram, orig_dir)
            temp_diag_lan = getattr(temp_diag_dir, "LAN")
            temp_diag_arr = getattr(temp_diag_lan, arrow)
            print(arrow, " : ", temp_diag_arr)


class VolumesForm(QtWidgets.QWidget):
    def __init__(self, mainDiagram, tempDiagram, orig_direction):
        QtWidgets.QWidget.__init__(self)

        # different variables for inner purposes
        self.mainDiagram = mainDiagram
        self.tempDiagram = tempDiagram
        self.or_dir = orig_direction

        self.ui_form = Volumes_Ui_Form()
        self.ui_form.setupUi(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.ui_form.shadow = QGraphicsDropShadowEffect(self)
        self.ui_form.shadow.setBlurRadius(10)
        self.ui_form.shadow.setXOffset(0)
        self.ui_form.shadow.setYOffset(0)
        self.ui_form.shadow.setColor(QColor(1, 1, 1))
        self.setGraphicsEffect(self.ui_form.shadow)
        self.ui_form.f_table_toolbar.mouseMoveEvent = self.moveForm
        self.ui_form.b_close_table.clicked.connect(lambda: self.closeWindow())
        self.ui_form.b_clear_all.clicked.connect(lambda: self.clearAll())
        self.ui_form.b_accept_table.clicked.connect(lambda: self.updateTableToDiagram())
        self.setVolOnlyNums()
        self.ui_form.mor_l.textEdited.connect(lambda: self.regularUpdateLabel(self.or_dir, self.ui_form.mor_l))
        self.ui_form.mor_t.textChanged.connect(lambda: self.regularUpdateLabel(self.or_dir, self.ui_form.mor_t))
        self.ui_form.mor_r.textChanged.connect(lambda: self.regularUpdateLabel(self.or_dir, self.ui_form.mor_r))
        self.ui_form.eve_l.textChanged.connect(lambda: self.regularUpdateLabel(self.or_dir, self.ui_form.eve_l))
        self.ui_form.eve_t.textChanged.connect(lambda: self.regularUpdateLabel(self.or_dir, self.ui_form.eve_t))
        self.ui_form.eve_r.textChanged.connect(lambda: self.regularUpdateLabel(self.or_dir, self.ui_form.eve_r))

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()

    def moveForm(self, e):
        if not self.isMaximized():
            if e.buttons() == QtCore.Qt.LeftButton:
                self.move(self.pos() + e.globalPos() - self.clickPosition)
                self.clickPosition = e.globalPos()
                e.accept()

    def closeWindow(self):
        self.TableUpdateToWindow()
        self.close()

    def updateTableToDiagram(self):
        window.changes_made = True
        orig_dir = self.or_dir
        all_times = ["MOR", "EVE"]
        all_sides = ["L", "T", "R"]
        temp_options = ["", "0", 0, "-"]
        for time in all_times:
            for side in all_sides:
                temp_diag_dir = getattr(self.tempDiagram, orig_dir)
                temp_diag_time = getattr(temp_diag_dir, time)
                temp_diag_side = getattr(temp_diag_time, side)

                main_diag_dir = getattr(self.mainDiagram, orig_dir)
                main_diag_time = getattr(main_diag_dir, time)
                setattr(main_diag_time, side, int(temp_diag_side))

                create_dir = "dig_" + orig_dir.lower() + "_vol_" + time.lower() + "_" + side.lower()
                update_ui = getattr(window, "ui")

                update_diagram = getattr(update_ui, create_dir)
                if temp_diag_side in temp_options:
                    temp_diag_side = "-"
                else:
                    temp_diag_side = int(temp_diag_side)

                update_diagram.setText(str(temp_diag_side))

                update_diagram.update()
                update_diagram.repaint()
        window.ToggleDirections()
        self.close()

    def TableUpdateToWindow(self):
        orig_dir = self.or_dir
        all_times = ["MOR", "EVE"]
        all_sides = ["L", "T", "R"]
        for time in all_times:
            for side in all_sides:
                main_diag_dir = getattr(self.mainDiagram, orig_dir)
                main_diag_time = getattr(main_diag_dir, time)
                main_diag_side = getattr(main_diag_time, side)

                temp_diag_dir = getattr(self.tempDiagram, orig_dir)
                temp_diag_time = getattr(temp_diag_dir, time)
                setattr(temp_diag_time, side, main_diag_side)

                if main_diag_side == "-":
                    main_diag_side = "0"
                else:
                    main_diag_side = str(main_diag_side)

                time_side = time.lower() + "_" + side.lower()

                update_diagram = getattr(self.ui_form, time_side)
                update_diagram.setText(main_diag_side)
                update_diagram.update()
                update_diagram.repaint()

    def clearAll(self):
        orig_dir = self.or_dir
        all_times = ["MOR", "EVE"]
        all_sides = ["L", "T", "R"]
        for time in all_times:
            for side in all_sides:
                temp_diag_dir = getattr(self.tempDiagram, orig_dir)
                temp_diag_time = getattr(temp_diag_dir, time)
                setattr(temp_diag_time, side, 0)
                time_side = time.lower() + "_" + side.lower()
                update_diagram = getattr(self.ui_form, time_side)
                update_diagram.setText("0")
                update_diagram.update()
                update_diagram.repaint()

    def setVolOnlyNums(self):
        all_times = ["mor_", "eve_"]
        all_sides = ["l", "t", "r"]
        for time in all_times:
            for side in all_sides:
                l_vol = getattr(self.ui_form, time + side)
                l_vol.setValidator(QRegExpValidator(QRegExp("[0-9]*"), l_vol))

    def regularUpdateLabel(self, orig_dir, l_vol):
        vol_time = l_vol.objectName().split("_")[0].upper()
        vol_side = l_vol.objectName().split("_")[-1].upper()
        diag_dir = getattr(self.tempDiagram, orig_dir)
        diag_time = getattr(diag_dir, vol_time)
        setattr(diag_time, vol_side, l_vol.text())


class LoadingForm(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.ui_form = Loading_Form()
        self.ui_form.setupUi(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.ui_form.shadow = QGraphicsDropShadowEffect(self)
        self.ui_form.shadow.setBlurRadius(10)
        self.ui_form.shadow.setXOffset(0)
        self.ui_form.shadow.setYOffset(0)
        self.ui_form.shadow.setColor(QColor(1, 1, 1))
        self.setGraphicsEffect(self.ui_form.shadow)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())

"""

"""
