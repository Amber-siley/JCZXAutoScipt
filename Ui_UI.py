# Form implementation generated from reading ui file 'e:\IDE\pyththon_project\jczx_auto_script\jczx\UI.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(576, 264)
        Form.setMinimumSize(QtCore.QSize(400, 264))
        Form.setMaximumSize(QtCore.QSize(576, 284))
        Form.setStyleSheet("QWidget {\n"
"    color: black;\n"
"    border: 1px;\n"
"    background-color: white;\n"
"}\n"
"QLineEdit {\n"
"    border: 1px solid rgb(153, 153, 153);\n"
"    border-radius: 2px;\n"
"}\n"
"QSpinBox {\n"
"    border: 1px solid rgb(153, 153, 153);\n"
"    background-color: white;\n"
"}")
        self.adb_path_label = QtWidgets.QLabel(parent=Form)
        self.adb_path_label.setGeometry(QtCore.QRect(0, 0, 71, 24))
        self.adb_path_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.adb_path_label.setIndent(-1)
        self.adb_path_label.setObjectName("adb_path_label")
        self.adb_path_lineEdit = QtWidgets.QLineEdit(parent=Form)
        self.adb_path_lineEdit.setGeometry(QtCore.QRect(70, 0, 306, 24))
        self.adb_path_lineEdit.setObjectName("adb_path_lineEdit")
        self.adb_devices_label = QtWidgets.QLabel(parent=Form)
        self.adb_devices_label.setGeometry(QtCore.QRect(0, 24, 71, 24))
        self.adb_devices_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.adb_devices_label.setIndent(-1)
        self.adb_devices_label.setObjectName("adb_devices_label")
        self.choice_adbpath_Button = QtWidgets.QPushButton(parent=Form)
        self.choice_adbpath_Button.setGeometry(QtCore.QRect(354, 0, 24, 24))
        self.choice_adbpath_Button.setStyleSheet("QPushButton {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #dcdfe6;\n"
"    border-radius: 1px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #ecf5ff;\n"
"    color: #409eff;\n"
"}\n"
"\n"
"QPushButton:pressed, QPushButton:checked {\n"
"    border: 1px solid #3a8ee6;\n"
"    color: #409eff;\n"
"}")
        self.choice_adbpath_Button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("C:/ProgramData/Microsoft/Device Stage/Task/{e35be42d-f742-4d96-a50a-1775fb1a7a42}/folder.ico"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.choice_adbpath_Button.setIcon(icon)
        self.choice_adbpath_Button.setObjectName("choice_adbpath_Button")
        self.authername_label = QtWidgets.QLabel(parent=Form)
        self.authername_label.setEnabled(True)
        self.authername_label.setGeometry(QtCore.QRect(0, 264, 577, 20))
        self.authername_label.setStyleSheet("QLabel {\n"
"    color: rgb(200, 200, 200)\n"
"}")
        self.authername_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.authername_label.setIndent(10)
        self.authername_label.setObjectName("authername_label")
        self.logger_Browser = QtWidgets.QTextBrowser(parent=Form)
        self.logger_Browser.setGeometry(QtCore.QRect(175, 24, 225, 241))
        self.logger_Browser.setStyleSheet("QTextBrowser {\n"
"    color: white;\n"
"    background-color:  black;\n"
"    border: 2px solid rgb(238, 238, 238);\n"
"    border-radius: 1px;\n"
"}")
        self.logger_Browser.setObjectName("logger_Browser")
        self.quarry_time_label = QtWidgets.QLabel(parent=Form)
        self.quarry_time_label.setGeometry(QtCore.QRect(0, 48, 71, 24))
        self.quarry_time_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.quarry_time_label.setIndent(-1)
        self.quarry_time_label.setObjectName("quarry_time_label")
        self.quarry_time_lineEdit = QtWidgets.QLineEdit(parent=Form)
        self.quarry_time_lineEdit.setGeometry(QtCore.QRect(70, 48, 105, 24))
        self.quarry_time_lineEdit.setText("")
        self.quarry_time_lineEdit.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.quarry_time_lineEdit.setObjectName("quarry_time_lineEdit")
        self.minute_unit_label = QtWidgets.QLabel(parent=Form)
        self.minute_unit_label.setGeometry(QtCore.QRect(150, 48, 25, 24))
        self.minute_unit_label.setStyleSheet("QLabel {\n"
"    border-bottom: 1px solid black;\n"
"}")
        self.minute_unit_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.minute_unit_label.setIndent(-1)
        self.minute_unit_label.setObjectName("minute_unit_label")
        self.save_config_Button = QtWidgets.QPushButton(parent=Form)
        self.save_config_Button.setGeometry(QtCore.QRect(0, 216, 175, 48))
        self.save_config_Button.setStyleSheet("QPushButton {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #dcdfe6;\n"
"    border-radius: 1px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: rgb(226, 255, 233);\n"
"    color: #409eff;\n"
"}\n"
"\n"
"QPushButton:pressed, QPushButton:checked {\n"
"    border: 1px solid #3a8ee6;\n"
"    color: #409eff;\n"
"}")
        self.save_config_Button.setObjectName("save_config_Button")
        self.start_switch_work_Button = QtWidgets.QPushButton(parent=Form)
        self.start_switch_work_Button.setGeometry(QtCore.QRect(0, 120, 175, 48))
        self.start_switch_work_Button.setStyleSheet("QPushButton {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #dcdfe6;\n"
"    border-radius: 1px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #ecf5ff;\n"
"    color: #409eff;\n"
"}\n"
"\n"
"QPushButton:pressed, QPushButton:checked {\n"
"    border: 1px solid #3a8ee6;\n"
"    color: #409eff;\n"
"}")
        self.start_switch_work_Button.setObjectName("start_switch_work_Button")
        self.start_spend_order_Button = QtWidgets.QPushButton(parent=Form)
        self.start_spend_order_Button.setGeometry(QtCore.QRect(0, 72, 175, 48))
        self.start_spend_order_Button.setStyleSheet("QPushButton {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #dcdfe6;\n"
"    border-radius: 1px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #ecf5ff;\n"
"    color: #409eff;\n"
"}\n"
"\n"
"QPushButton:pressed, QPushButton:checked {\n"
"    border: 1px solid #3a8ee6;\n"
"    color: #409eff;\n"
"}")
        self.start_spend_order_Button.setObjectName("start_spend_order_Button")
        self.stop_all_task_Button = QtWidgets.QPushButton(parent=Form)
        self.stop_all_task_Button.setGeometry(QtCore.QRect(0, 168, 175, 48))
        self.stop_all_task_Button.setStyleSheet("QPushButton {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #dcdfe6;\n"
"    border-radius: 1px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: rgb(255, 239, 239);\n"
"    color: rgb(255, 32, 36);\n"
"}\n"
"\n"
"QPushButton:pressed, QPushButton:checked {\n"
"    border: 1px solid #3a8ee6;\n"
"    color: #409eff;\n"
"}")
        self.stop_all_task_Button.setObjectName("stop_all_task_Button")
        self.oder_list_label = QtWidgets.QLabel(parent=Form)
        self.oder_list_label.setGeometry(QtCore.QRect(400, 0, 121, 24))
        self.oder_list_label.setToolTip("")
        self.oder_list_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.oder_list_label.setIndent(-1)
        self.oder_list_label.setObjectName("oder_list_label")
        self.order_build61_checkBox = QtWidgets.QCheckBox(parent=Form)
        self.order_build61_checkBox.setGeometry(QtCore.QRect(400, 24, 121, 20))
        self.order_build61_checkBox.setStyleSheet("QCheckBox {\n"
"    border-top: 1px solid black;\n"
"    border-bottom: 1px solid black;\n"
"}")
        self.order_build61_checkBox.setShortcut("")
        self.order_build61_checkBox.setCheckable(True)
        self.order_build61_checkBox.setChecked(True)
        self.order_build61_checkBox.setAutoRepeat(False)
        self.order_build61_checkBox.setTristate(False)
        self.order_build61_checkBox.setObjectName("order_build61_checkBox")
        self.order_build81_checkBox = QtWidgets.QCheckBox(parent=Form)
        self.order_build81_checkBox.setGeometry(QtCore.QRect(400, 44, 121, 20))
        self.order_build81_checkBox.setStyleSheet("QCheckBox {\n"
"    border-bottom: 1px solid black;\n"
"}")
        self.order_build81_checkBox.setShortcut("")
        self.order_build81_checkBox.setCheckable(True)
        self.order_build81_checkBox.setChecked(True)
        self.order_build81_checkBox.setAutoRepeat(False)
        self.order_build81_checkBox.setTristate(False)
        self.order_build81_checkBox.setObjectName("order_build81_checkBox")
        self.order_build162_checkBox = QtWidgets.QCheckBox(parent=Form)
        self.order_build162_checkBox.setGeometry(QtCore.QRect(400, 84, 121, 20))
        self.order_build162_checkBox.setStyleSheet("QCheckBox {\n"
"    border-bottom: 1px solid black;\n"
"}")
        self.order_build162_checkBox.setShortcut("")
        self.order_build162_checkBox.setCheckable(True)
        self.order_build162_checkBox.setChecked(True)
        self.order_build162_checkBox.setAutoRepeat(False)
        self.order_build162_checkBox.setTristate(False)
        self.order_build162_checkBox.setObjectName("order_build162_checkBox")
        self.order_build182_checkBox = QtWidgets.QCheckBox(parent=Form)
        self.order_build182_checkBox.setGeometry(QtCore.QRect(400, 104, 121, 20))
        self.order_build182_checkBox.setStyleSheet("QCheckBox {\n"
"    border-bottom: 1px solid black;\n"
"}")
        self.order_build182_checkBox.setShortcut("")
        self.order_build182_checkBox.setCheckable(True)
        self.order_build182_checkBox.setChecked(True)
        self.order_build182_checkBox.setAutoRepeat(False)
        self.order_build182_checkBox.setTristate(False)
        self.order_build182_checkBox.setObjectName("order_build182_checkBox")
        self.order_build101_checkBox = QtWidgets.QCheckBox(parent=Form)
        self.order_build101_checkBox.setGeometry(QtCore.QRect(400, 64, 121, 20))
        self.order_build101_checkBox.setStyleSheet("QCheckBox {\n"
"    border-bottom: 1px solid black;\n"
"}")
        self.order_build101_checkBox.setShortcut("")
        self.order_build101_checkBox.setCheckable(True)
        self.order_build101_checkBox.setChecked(False)
        self.order_build101_checkBox.setAutoRepeat(False)
        self.order_build101_checkBox.setTristate(False)
        self.order_build101_checkBox.setObjectName("order_build101_checkBox")
        self.order_coin1012w_checkBox = QtWidgets.QCheckBox(parent=Form)
        self.order_coin1012w_checkBox.setGeometry(QtCore.QRect(400, 124, 121, 20))
        self.order_coin1012w_checkBox.setStyleSheet("QCheckBox {\n"
"    border-bottom: 1px solid black;\n"
"}")
        self.order_coin1012w_checkBox.setShortcut("")
        self.order_coin1012w_checkBox.setCheckable(True)
        self.order_coin1012w_checkBox.setChecked(False)
        self.order_coin1012w_checkBox.setAutoRepeat(False)
        self.order_coin1012w_checkBox.setTristate(False)
        self.order_coin1012w_checkBox.setObjectName("order_coin1012w_checkBox")
        self.order_exp1012w_checkBox = QtWidgets.QCheckBox(parent=Form)
        self.order_exp1012w_checkBox.setGeometry(QtCore.QRect(400, 144, 121, 20))
        self.order_exp1012w_checkBox.setStyleSheet("QCheckBox {\n"
"    border-bottom: 1px solid black;\n"
"}")
        self.order_exp1012w_checkBox.setShortcut("")
        self.order_exp1012w_checkBox.setCheckable(True)
        self.order_exp1012w_checkBox.setChecked(False)
        self.order_exp1012w_checkBox.setAutoRepeat(False)
        self.order_exp1012w_checkBox.setTristate(False)
        self.order_exp1012w_checkBox.setObjectName("order_exp1012w_checkBox")
        self.spinBox = QtWidgets.QSpinBox(parent=Form)
        self.spinBox.setGeometry(QtCore.QRect(520, 24, 61, 20))
        self.spinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.spinBox.setObjectName("spinBox")
        self.oder_num_label = QtWidgets.QLabel(parent=Form)
        self.oder_num_label.setGeometry(QtCore.QRect(520, 0, 60, 24))
        self.oder_num_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.oder_num_label.setIndent(-1)
        self.oder_num_label.setObjectName("oder_num_label")
        self.spinBox_2 = QtWidgets.QSpinBox(parent=Form)
        self.spinBox_2.setGeometry(QtCore.QRect(520, 44, 61, 20))
        self.spinBox_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.spinBox_2.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.spinBox_2.setObjectName("spinBox_2")
        self.spinBox_3 = QtWidgets.QSpinBox(parent=Form)
        self.spinBox_3.setGeometry(QtCore.QRect(520, 64, 61, 20))
        self.spinBox_3.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.spinBox_3.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.spinBox_3.setObjectName("spinBox_3")
        self.spinBox_4 = QtWidgets.QSpinBox(parent=Form)
        self.spinBox_4.setGeometry(QtCore.QRect(520, 84, 61, 20))
        self.spinBox_4.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.spinBox_4.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.spinBox_4.setObjectName("spinBox_4")
        self.spinBox_5 = QtWidgets.QSpinBox(parent=Form)
        self.spinBox_5.setGeometry(QtCore.QRect(520, 104, 61, 20))
        self.spinBox_5.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.spinBox_5.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.spinBox_5.setObjectName("spinBox_5")
        self.spinBox_6 = QtWidgets.QSpinBox(parent=Form)
        self.spinBox_6.setGeometry(QtCore.QRect(520, 124, 61, 20))
        self.spinBox_6.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.spinBox_6.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.spinBox_6.setObjectName("spinBox_6")
        self.spinBox_7 = QtWidgets.QSpinBox(parent=Form)
        self.spinBox_7.setGeometry(QtCore.QRect(520, 144, 61, 20))
        self.spinBox_7.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.spinBox_7.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.spinBox_7.setObjectName("spinBox_7")
        self.order_t3YJZJ_151_checkBox = QtWidgets.QCheckBox(parent=Form)
        self.order_t3YJZJ_151_checkBox.setGeometry(QtCore.QRect(400, 164, 121, 20))
        self.order_t3YJZJ_151_checkBox.setStyleSheet("QCheckBox {\n"
"    border-bottom: 1px solid black;\n"
"}")
        self.order_t3YJZJ_151_checkBox.setShortcut("")
        self.order_t3YJZJ_151_checkBox.setCheckable(False)
        self.order_t3YJZJ_151_checkBox.setChecked(False)
        self.order_t3YJZJ_151_checkBox.setAutoRepeat(False)
        self.order_t3YJZJ_151_checkBox.setTristate(False)
        self.order_t3YJZJ_151_checkBox.setObjectName("order_t3YJZJ_151_checkBox")
        self.spinBox_8 = QtWidgets.QSpinBox(parent=Form)
        self.spinBox_8.setGeometry(QtCore.QRect(520, 164, 61, 20))
        self.spinBox_8.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.spinBox_8.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.spinBox_8.setObjectName("spinBox_8")
        self.spinBox_9 = QtWidgets.QSpinBox(parent=Form)
        self.spinBox_9.setGeometry(QtCore.QRect(520, 184, 61, 20))
        self.spinBox_9.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.spinBox_9.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.spinBox_9.setObjectName("spinBox_9")
        self.order_t3YJBDT_151_checkBox = QtWidgets.QCheckBox(parent=Form)
        self.order_t3YJBDT_151_checkBox.setGeometry(QtCore.QRect(400, 184, 121, 20))
        self.order_t3YJBDT_151_checkBox.setStyleSheet("QCheckBox {\n"
"    border-bottom: 1px solid black;\n"
"}")
        self.order_t3YJBDT_151_checkBox.setShortcut("")
        self.order_t3YJBDT_151_checkBox.setCheckable(False)
        self.order_t3YJBDT_151_checkBox.setChecked(False)
        self.order_t3YJBDT_151_checkBox.setAutoRepeat(False)
        self.order_t3YJBDT_151_checkBox.setTristate(False)
        self.order_t3YJBDT_151_checkBox.setObjectName("order_t3YJBDT_151_checkBox")
        self.spinBox_10 = QtWidgets.QSpinBox(parent=Form)
        self.spinBox_10.setGeometry(QtCore.QRect(520, 204, 61, 20))
        self.spinBox_10.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.spinBox_10.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.spinBox_10.setObjectName("spinBox_10")
        self.order_t3YJHJ_151_checkBox = QtWidgets.QCheckBox(parent=Form)
        self.order_t3YJHJ_151_checkBox.setGeometry(QtCore.QRect(400, 204, 121, 20))
        self.order_t3YJHJ_151_checkBox.setStyleSheet("QCheckBox {\n"
"    border-bottom: 1px solid black;\n"
"}")
        self.order_t3YJHJ_151_checkBox.setShortcut("")
        self.order_t3YJHJ_151_checkBox.setCheckable(False)
        self.order_t3YJHJ_151_checkBox.setChecked(False)
        self.order_t3YJHJ_151_checkBox.setAutoRepeat(False)
        self.order_t3YJHJ_151_checkBox.setTristate(False)
        self.order_t3YJHJ_151_checkBox.setObjectName("order_t3YJHJ_151_checkBox")
        self.order_t3NPJ_151_checkBox = QtWidgets.QCheckBox(parent=Form)
        self.order_t3NPJ_151_checkBox.setGeometry(QtCore.QRect(400, 224, 121, 20))
        self.order_t3NPJ_151_checkBox.setStyleSheet("QCheckBox {\n"
"    border-bottom: 1px solid black;\n"
"}")
        self.order_t3NPJ_151_checkBox.setShortcut("")
        self.order_t3NPJ_151_checkBox.setCheckable(False)
        self.order_t3NPJ_151_checkBox.setChecked(False)
        self.order_t3NPJ_151_checkBox.setAutoRepeat(False)
        self.order_t3NPJ_151_checkBox.setTristate(False)
        self.order_t3NPJ_151_checkBox.setObjectName("order_t3NPJ_151_checkBox")
        self.spinBox_11 = QtWidgets.QSpinBox(parent=Form)
        self.spinBox_11.setGeometry(QtCore.QRect(520, 224, 61, 20))
        self.spinBox_11.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.spinBox_11.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.spinBox_11.setObjectName("spinBox_11")
        self.spinBox_12 = QtWidgets.QSpinBox(parent=Form)
        self.spinBox_12.setGeometry(QtCore.QRect(520, 244, 61, 20))
        self.spinBox_12.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.spinBox_12.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.spinBox_12.setObjectName("spinBox_12")
        self.order_t3HJNY_151_checkBox = QtWidgets.QCheckBox(parent=Form)
        self.order_t3HJNY_151_checkBox.setGeometry(QtCore.QRect(400, 244, 121, 20))
        self.order_t3HJNY_151_checkBox.setStyleSheet("QCheckBox {\n"
"    border-bottom: 1px solid black;\n"
"}")
        self.order_t3HJNY_151_checkBox.setShortcut("")
        self.order_t3HJNY_151_checkBox.setCheckable(False)
        self.order_t3HJNY_151_checkBox.setChecked(False)
        self.order_t3HJNY_151_checkBox.setAutoRepeat(False)
        self.order_t3HJNY_151_checkBox.setTristate(False)
        self.order_t3HJNY_151_checkBox.setObjectName("order_t3HJNY_151_checkBox")
        self.adb_devices_comboBox = QtWidgets.QComboBox(parent=Form)
        self.adb_devices_comboBox.setGeometry(QtCore.QRect(70, 24, 105, 24))
        self.adb_devices_comboBox.setStyleSheet("QComboBox {\n"
"    border: 1px solid white;\n"
"    border-bottom: 1px solid rgb(153, 153, 153);\n"
"    border-left: 1px solid rgb(195, 195, 195);\n"
"}")
        self.adb_devices_comboBox.setObjectName("adb_devices_comboBox")
        self.test_button = QtWidgets.QPushButton(parent=Form)
        self.test_button.setGeometry(QtCore.QRect(220, 266, 141, 20))
        self.test_button.setStyleSheet("QPushButton {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #dcdfe6;\n"
"    border-radius: 1px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: rgb(226, 255, 233);\n"
"    color: #409eff;\n"
"}\n"
"\n"
"QPushButton:pressed, QPushButton:checked {\n"
"    border: 1px solid #3a8ee6;\n"
"    color: #409eff;\n"
"}")
        self.test_button.setObjectName("test_button")
        self.help_button = QtWidgets.QPushButton(parent=Form)
        self.help_button.setGeometry(QtCore.QRect(376, 0, 24, 24))
        self.help_button.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.help_button.setStyleSheet("QPushButton {\n"
"    color: rgb(168, 168, 168);\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #dcdfe6;\n"
"    border-radius: 1px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #ecf5ff;\n"
"    color: #409eff;\n"
"}\n"
"\n"
"QPushButton:pressed, QPushButton:checked {\n"
"    border: 1px solid #3a8ee6;\n"
"    color: #409eff;\n"
"}")
        self.help_button.setObjectName("help_button")
        self.help_textBrowser = QtWidgets.QTextBrowser(parent=Form)
        self.help_textBrowser.setGeometry(QtCore.QRect(400, 0, 181, 271))
        self.help_textBrowser.setObjectName("help_textBrowser")
        self.adb_path_label.raise_()
        self.adb_path_lineEdit.raise_()
        self.adb_devices_label.raise_()
        self.choice_adbpath_Button.raise_()
        self.authername_label.raise_()
        self.logger_Browser.raise_()
        self.quarry_time_label.raise_()
        self.quarry_time_lineEdit.raise_()
        self.minute_unit_label.raise_()
        self.save_config_Button.raise_()
        self.start_switch_work_Button.raise_()
        self.start_spend_order_Button.raise_()
        self.stop_all_task_Button.raise_()
        self.oder_list_label.raise_()
        self.order_build61_checkBox.raise_()
        self.order_build81_checkBox.raise_()
        self.order_build162_checkBox.raise_()
        self.order_build182_checkBox.raise_()
        self.order_build101_checkBox.raise_()
        self.order_coin1012w_checkBox.raise_()
        self.order_exp1012w_checkBox.raise_()
        self.oder_num_label.raise_()
        self.order_t3YJZJ_151_checkBox.raise_()
        self.order_t3YJBDT_151_checkBox.raise_()
        self.order_t3YJHJ_151_checkBox.raise_()
        self.order_t3NPJ_151_checkBox.raise_()
        self.order_t3HJNY_151_checkBox.raise_()
        self.adb_devices_comboBox.raise_()
        self.test_button.raise_()
        self.spinBox_12.raise_()
        self.spinBox_11.raise_()
        self.spinBox_10.raise_()
        self.spinBox_9.raise_()
        self.spinBox_8.raise_()
        self.spinBox_7.raise_()
        self.spinBox_6.raise_()
        self.spinBox_5.raise_()
        self.spinBox_4.raise_()
        self.spinBox_3.raise_()
        self.spinBox_2.raise_()
        self.spinBox.raise_()
        self.help_button.raise_()
        self.help_textBrowser.raise_()

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.adb_path_label.setText(_translate("Form", "ADB路径："))
        self.adb_devices_label.setText(_translate("Form", "设备列表："))
        self.choice_adbpath_Button.setToolTip(_translate("Form", "选择ADB调试程序"))
        self.authername_label.setText(_translate("Form", "Created by 思默fine"))
        self.quarry_time_label.setText(_translate("Form", "矿场结算："))
        self.quarry_time_lineEdit.setToolTip(_translate("Form", "第一次矿场结算时间 会自动获取"))
        self.minute_unit_label.setToolTip(_translate("Form", "第一次矿场结算时间 会自动获取"))
        self.minute_unit_label.setText(_translate("Form", "M"))
        self.save_config_Button.setToolTip(_translate("Form", "保存当前配置并应用"))
        self.save_config_Button.setText(_translate("Form", "保存用户配置"))
        self.start_switch_work_Button.setToolTip(_translate("Form", "先将矿场员工换班，然后在规定时间巡查订单库进行提交"))
        self.start_switch_work_Button.setText(_translate("Form", "启动换班任务"))
        self.start_spend_order_Button.setToolTip(_translate("Form", "寻找订单并交付"))
        self.start_spend_order_Button.setText(_translate("Form", "启动交付订单"))
        self.stop_all_task_Button.setToolTip(_translate("Form", "停止脚本操作游戏"))
        self.stop_all_task_Button.setText(_translate("Form", "停止所有任务"))
        self.oder_list_label.setText(_translate("Form", " 订单列表"))
        self.order_build61_checkBox.setText(_translate("Form", "6换1构建"))
        self.order_build81_checkBox.setText(_translate("Form", "8换1构建"))
        self.order_build162_checkBox.setText(_translate("Form", "16换2构建"))
        self.order_build182_checkBox.setText(_translate("Form", "18换2构建"))
        self.order_build101_checkBox.setText(_translate("Form", "10换1构建"))
        self.order_coin1012w_checkBox.setText(_translate("Form", "10换12w星币"))
        self.order_exp1012w_checkBox.setText(_translate("Form", "10换12w经验"))
        self.oder_num_label.setToolTip(_translate("Form", "每天订单换取次数 限制为0时无限制"))
        self.oder_num_label.setText(_translate("Form", "数量限制"))
        self.order_t3YJZJ_151_checkBox.setText(_translate("Form", "15换1亚金组件 T3"))
        self.order_t3YJBDT_151_checkBox.setText(_translate("Form", "15换1亚金导体 T3"))
        self.order_t3YJHJ_151_checkBox.setText(_translate("Form", "15换1亚金合金 T3"))
        self.order_t3NPJ_151_checkBox.setText(_translate("Form", "15换1涅槃剂 T3"))
        self.order_t3HJNY_151_checkBox.setText(_translate("Form", "15换1幻金能源 T3"))
        self.test_button.setToolTip(_translate("Form", "test"))
        self.test_button.setText(_translate("Form", "test"))
        self.help_button.setToolTip(_translate("Form", "帮助"))
        self.help_button.setText(_translate("Form", "?"))
        self.help_textBrowser.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:\'Microsoft YaHei UI\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">ADB路径：模拟器目录下的ADB.exe调试程序路径</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">设备列表：模拟器下的设备，默认获取第一个设备</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">矿场结算：矿场每30分钟结算一次矿物，值与账号注册时间有关，当没有指定设置或者为-1时，自动挂机30分钟获取时间</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">启动交付订单：首先检查订单库并交付符合条件的订单，再进行矿场换班工作</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">启动换班任务：首先进行矿场换班工作，再进行在规定时间进行交付订单任务</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">保存用户配置：使用手动修改方式并不会触发自动保存，推荐修改配置项后手动保存配置</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
