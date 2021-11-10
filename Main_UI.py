import ctypes
import os
import sys
from screeninfo import get_monitors
from PyQt5.QtCore import QPropertyAnimation, QRegExp, Qt, QRect, QEasingCurve
from PyQt5.QtGui import QColor, QPainter, QRegExpValidator, QFont, QBrush, QPalette, QGuiApplication, QScreen
from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsDropShadowEffect, QFileDialog, QMessageBox, \
    QDesktopWidget, QCheckBox, QGraphicsBlurEffect
# from pydeck import settings
# from win32api import GetSystemMetrics

from Diagram import Diagram
from JUCSON import Jucson
from VOLCOV import VolCov
from ui_main_withside_nosidebar import *
from ui_window_arrows_with_complex import *
from ui_window_volumes import *
import Main_ID


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

        self.ui.no_name.textEdited.connect(lambda: self.updateNamesToMainDiagram("no"))
        self.ui.so_name.textEdited.connect(lambda: self.updateNamesToMainDiagram("so"))
        self.ui.ea_name.textEdited.connect(lambda: self.updateNamesToMainDiagram("ea"))
        self.ui.we_name.textEdited.connect(lambda: self.updateNamesToMainDiagram("we"))

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

        self.ui.b_destfolder.clicked.connect(lambda: self.setOutputDirectory())

        self.ui.no_check.setChecked(True)
        self.ui.ea_check.setChecked(True)
        self.ui.we_check.setChecked(True)
        self.ui.so_check.setChecked(True)

        self.ui.no_check.clicked.connect(lambda: self.ToggleNO())
        self.ui.ea_check.clicked.connect(lambda: self.ToggleEA())
        self.ui.we_check.clicked.connect(lambda: self.ToggleWE())
        self.ui.so_check.clicked.connect(lambda: self.ToggleSO())

        # Direction animations

        self.anim_no_h = QPropertyAnimation(self.ui.f_dig_no, b"maximumHeight")
        self.anim_so_h = QPropertyAnimation(self.ui.f_dig_so, b"maximumHeight")
        self.anim_ea_h = QPropertyAnimation(self.ui.f_dig_ea, b"maximumHeight")
        self.anim_we_h = QPropertyAnimation(self.ui.f_dig_we, b"maximumHeight")
        self.anim_no_w = QPropertyAnimation(self.ui.f_dig_no, b"minimumWidth")
        self.anim_so_w = QPropertyAnimation(self.ui.f_dig_so, b"minimumWidth")
        self.anim_ea_w = QPropertyAnimation(self.ui.f_dig_ea, b"minimumWidth")
        self.anim_we_w = QPropertyAnimation(self.ui.f_dig_we, b"minimumWidth")

        # fix screen sizing #

        self.ui.b_run.clicked.connect(lambda: self.run_JUNC())

        self.tempAuthor = ""
        self.setMonitorSize()
        self.rotate_pixmap()
        self.ui.b_open_close_edit.checkedState = False
        self.ui.b_open_close_edit.setText("W")
        self.ui.f_edit_control_buttons.setMaximumWidth(0)
        self.show()
        self.rotate_pixmap()
        self.editSize()

        #  Edit menu info

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

        # First Page
        self.ui.txt_pro_name.textEdited.connect(lambda: self.setProjectName())
        self.ui.txt_pro_num.textEdited.connect(lambda: self.setProjectNumber())
        self.ui.txt_author.textEdited.connect(lambda: self.setAuthorName())
        self.ui.check_get_username.clicked.connect(lambda: self.checkBoxAuthor())
        self.ui.txt_ver.textEdited.connect(lambda: self.setCount())
        self.ui.txt_info.textEdited.connect(lambda: self.setMoreInfo())

        # Second Page

        # Third Page

        self.ui.b_update.clicked.connect(lambda: self.printPhaserList())

    def run_JUNC(self):
        Main_ID.set_Diagram(self.mainDiagram)
        final_message = Main_ID.main()
        msgBox = QMessageBox()
        msgBox.setText(final_message)
        msgBox.exec()


    def setProjectName(self):
        self.phaser_input_list[21][0] = self.ui.txt_pro_name.text()

    def setProjectNumber(self):
        self.phaser_input_list[21][1] = self.ui.txt_pro_num.text()

    def checkBoxAuthor(self):
        if self.ui.check_get_username.isChecked():
            self.ui.txt_author.setText(self.current_user_name)
        else:
            self.ui.txt_author.setText(self.tempAuthor)
        self.setAuthorName()

    def setAuthorName(self):
        if not self.ui.check_get_username.isChecked():
            self.tempAuthor = self.ui.txt_author.text()
        self.phaser_input_list[21][2] = self.ui.txt_author.text()

    def setCount(self):
        self.phaser_input_list[21][3] = self.ui.txt_ver.text()

    def setMoreInfo(self):
        self.phaser_input_list[21][4] = self.ui.txt_info.text()

    def printPhaserList(self):
        print(self.phaser_input_list[21])

    # Global functions

    def changeScreen(self):
        pass

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()

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
        if self.ui.no_check.isChecked():
            old_size = 0
            new_size = self.ui.f_dig_m.height()
        else:
            old_size = self.ui.f_dig_m.height()
            new_size = 0

        self.anim_no_h.setDuration(450)
        self.anim_no_h.setStartValue(old_size)
        self.anim_no_h.setEndValue(new_size)
        self.anim_no_h.setEasingCurve(QEasingCurve.InOutExpo)
        self.anim_no_h.start()

    def ToggleSO(self):
        if self.ui.so_check.isChecked():
            old_size = 0
            new_size = self.ui.f_dig_m.height()
        else:
            old_size = self.ui.f_dig_m.height()
            new_size = 0

        self.anim_so_h.setDuration(450)
        self.anim_so_h.setStartValue(old_size)
        self.anim_so_h.setEndValue(new_size)
        self.anim_so_h.setEasingCurve(QEasingCurve.InOutExpo)
        self.anim_so_h.start()

    def ToggleEA(self):
        if self.ui.ea_check.isChecked():
            old_size = 0
            new_size = self.ui.f_dig_m.height()
        else:
            old_size = self.ui.f_dig_m.height()
            new_size = 0

        self.anim_ea_w.setDuration(450)
        self.anim_ea_w.setStartValue(old_size)
        self.anim_ea_w.setEndValue(new_size)
        self.anim_ea_w.setEasingCurve(QEasingCurve.InOutExpo)
        self.anim_ea_w.start()

    def ToggleWE(self):
        if self.ui.we_check.isChecked():
            old_size = 0
            new_size = self.ui.f_dig_m.height()
        else:
            old_size = self.ui.f_dig_m.height()
            new_size = 0

        self.anim_we_w.setDuration(450)
        self.anim_we_w.setStartValue(old_size)
        self.anim_we_w.setEndValue(new_size)
        self.anim_we_w.setEasingCurve(QEasingCurve.InOutExpo)
        self.anim_we_w.start()

    def ShowHideEa(self):
        if self.ui.ea_check.isChecked():
            self.ui.f_dig_ea.show()
        else:
            self.ui.f_dig_ea.hide()

    def ShowHideWe(self):
        if self.ui.we_check.isChecked():
            self.ui.f_dig_we.show()
        else:
            self.ui.f_dig_we.hide()

    def ShowHideSo(self):
        if self.ui.so_check.isChecked():
            self.ui.f_dig_so.show()
        else:
            self.ui.f_dig_so.hide()

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
        f_digs = [[self.ui.no_check.isChecked(), self.anim_no_h, self.anim_no_w],
                  [self.ui.so_check.isChecked(), self.anim_so_h, self.anim_so_w],
                  [self.ui.ea_check.isChecked(), self.anim_ea_h, self.anim_ea_w],
                  [self.ui.we_check.isChecked(), self.anim_we_h, self.anim_we_w]]
        self.anim_no_h = QPropertyAnimation(self.ui.f_dig_no, b"maximumHeight")
        self.anim_so_h = QPropertyAnimation(self.ui.f_dig_so, b"maximumHeight")
        self.anim_ea_h = QPropertyAnimation(self.ui.f_dig_ea, b"maximumHeight")
        self.anim_we_h = QPropertyAnimation(self.ui.f_dig_we, b"maximumHeight")
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
            print("app_height: ", self.app_height)
            app_width = int(round(self.app_height * app_width_height_ratio, 0))
            self.setFixedHeight(self.app_height)
            self.setFixedWidth(app_width)
        self.editDiagramSize()

    def setMonitorSize(self):
        for m in get_monitors():
            self.allMonitors[int(not m.is_primary)] = [m.height, m.width]
        print(self.allMonitors)

    def slideRightMenu(self):
        width = self.ui.slide_menu_container.width()

        if width == 0:
            oldWindowWidth = 1244
            newWindowWidth = 1594
            newWidth = 350

            self.ui.menu_button.setText("W")
            self.ui.body_header.setStyleSheet(
                'QFrame#body_header{background-color: rgb(55, 62, 78);border-top-left-radius: 25px;}')

        else:
            newWidth = 0
            newWindowWidth = 1244
            oldWindowWidth = 1594
            window_size = "S"
            self.ui.menu_button.setText("L")
            self.ui.body_header.setStyleSheet(
                'QFrame#body_header{background-color: rgb(55, 62, 78);border-top-right-radius: '
                '25px;border-top-left-radius: 25px;}')

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
            return ""
        elif reply == QMessageBox.No:
            return ""

        elif reply == QMessageBox.Cancel:
            return "cancel"

    def createNewMessageBox(self):
        button_value = self.saveMessageBox("new")
        if button_value == "cancel":
            return
        else:
            directory = os.getcwd() + r"\clear_dont_delete.json"
            self.jucson.loadJucson(directory)
            self.updateMainDiagramFromJucson()

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
        print(self.mainDiagram.OUTPUT)
        location = str(QFileDialog.getExistingDirectory(self, "בחירת מיקום לייצוא הקובץ הסופי"))
        if location == "":
            msgBox = QMessageBox()
            msgBox.setText("יש לבחור מיקום לייצוא הקובץ הסופי")
            msgBox.exec()
            return ""
        else:

            self.mainDiagram.OUTPUT = location.replace("/", "\\")
            print(self.mainDiagram.OUTPUT)

    def updateMainDiagramFromJucson(self):
        jucson_methods = ["push_id_info", "push_arr", "push_vol", "push_general_info", "push_lrt_info",
                          "push_street_names"]
        for method in jucson_methods:
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
            form.ui_form.window_name_arrows.setText(self.ui.no_name.text())
            form.ui_form.window_name_arrows.update()
            form.ui_form.window_name_arrows.repaint()
            form.checkingOptionUpdate()
            form.show()
            form.updateToWindow("NO")
            self.ui.dig_no_arrows.update()
            self.ui.dig_no_arrows.repaint()

    def openEastArrows(self, form):

        if form.isVisible():
            form.activateWindow()
        else:
            form.ui_form.window_name_arrows.setText(self.ui.ea_name.text())
            form.ui_form.window_name_arrows.update()
            form.ui_form.window_name_arrows.repaint()
            form.checkingOptionUpdate()
            form.show()
            form.updateToWindow("EA")
            self.ui.dig_ea_arrows.update()
            self.ui.dig_ea_arrows.repaint()

    def openSouthArrows(self, form):

        if form.isVisible():
            form.activateWindow()
        else:
            form.ui_form.window_name_arrows.setText("REDE")
            form.ui_form.window_name_arrows.update()
            form.ui_form.window_name_arrows.repaint()
            form.checkingOptionUpdate()
            form.show()
            form.updateToWindow("SO")
            self.ui.dig_so_arrows.update()
            self.ui.dig_so_arrows.repaint()

    def openWestArrows(self, form):

        if form.isVisible():
            form.activateWindow()
        else:
            form.ui_form.window_name_arrows.setText(self.ui.we_name.text())
            form.ui_form.window_name_arrows.update()
            form.ui_form.window_name_arrows.repaint()
            form.checkingOptionUpdate()
            form.show()
            form.updateToWindow("WE")
            self.ui.dig_we_arrows.update()
            self.ui.dig_we_arrows.repaint()

    def openNorthVolumes(self, form):

        if form.isVisible():
            form.activateWindow()
        else:
            form.ui_form.window_name_volumes.setText(self.ui.no_name.text())
            form.ui_form.window_name_volumes.update()
            form.ui_form.window_name_volumes.repaint()
            form.TableUpdateToWindow()
            form.show()

    def openEastVolumes(self, form):

        if form.isVisible():
            form.activateWindow()
        else:
            form.ui_form.window_name_volumes.setText(self.ui.ea_name.text())
            form.ui_form.window_name_volumes.update()
            form.ui_form.window_name_volumes.repaint()
            form.TableUpdateToWindow()
            form.show()

    def openSouthVolumes(self, form):

        if form.isVisible():
            form.activateWindow()
        else:
            form.ui_form.window_name_volumes.setText(self.ui.so_name.text())
            form.ui_form.window_name_volumes.update()
            form.ui_form.window_name_volumes.repaint()
            form.TableUpdateToWindow()
            form.show()

    def openWestVolumes(self, form):

        if form.isVisible():
            form.activateWindow()
        else:

            form.ui_form.window_name_volumes.setText(self.ui.we_name.text())
            form.ui_form.window_name_volumes.update()
            form.ui_form.window_name_volumes.repaint()
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
        self.ui_form.b_accept_table.clicked.connect(lambda: self.updateToDiagram())
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

    def updateToDiagram(self):
        window.changes_made = True
        orig_dir = self.or_dir
        all_times = ["MOR", "EVE"]
        all_sides = ["L", "T", "R"]
        temp_options = ["", "0", 0]
        for time in all_times:
            for side in all_sides:

                temp_diag_dir = getattr(self.tempDiagram, orig_dir)
                temp_diag_time = getattr(temp_diag_dir, time)
                temp_diag_side = getattr(temp_diag_time, side)

                main_diag_dir = getattr(self.mainDiagram, orig_dir)
                main_diag_time = getattr(main_diag_dir, time)
                setattr(main_diag_time, side, temp_diag_side)

                create_dir = "dig_" + orig_dir.lower() + "_vol_" + time.lower() + "_" + side.lower()
                update_ui = getattr(window, "ui")

                update_diagram = getattr(update_ui, create_dir)
                if temp_diag_side in temp_options:
                    temp_diag_side = "-"

                update_diagram.setText(str(temp_diag_side))

                update_diagram.update()
                update_diagram.repaint()

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
                setattr(temp_diag_time, side, "0")
                time_side = time.lower() + "_" + side.lower()

                update_diagram = getattr(self.ui_form, time_side)
                update_diagram.setText("")
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
