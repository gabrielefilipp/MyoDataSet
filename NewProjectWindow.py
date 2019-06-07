from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import *
from GestureListView import GestureListView
from MainWindow import MainWindow
import json
import os

HEIGHT = 500
WIDTH = 640

ll_ss = "QGroupBox {border: 1px solid gray;border-radius: 9px;margin-top: 0.5em;} QGroupBox::title {subcontrol-origin: margin;left: 10px;padding: 0 3px 0 3px;}"

class NewProjectWindow(QMainWindow):

    def __init__(self, parent=None):
        super(NewProjectWindow, self).__init__(parent)

        self.initUI()

    def initUI(self):
        self.setWindowTitle("New Dataset")
        self.setGeometry(240, 120, WIDTH, HEIGHT)
        self.setFixedSize(QSize(WIDTH, HEIGHT))

        group_path = QGroupBox(self)
        group_path.setStyleSheet(ll_ss)
        group_path.setTitle("Dataset path")
        group_path.setGeometry(15, 10, WIDTH - 30, 130)

        lbl = QLabel(group_path)
        lbl.setText("Name: ")
        lbl.setGeometry(20, 30, 50, 25)

        self.name = QLineEdit(group_path)
        self.name.setStyleSheet("border:none;border-radius:8px;background-color: palette(base);")
        self.name.setGeometry(80, 30, WIDTH - 135, 25)

        lbl = QLabel(group_path)
        lbl.setText("Path: ")
        lbl.setGeometry(20, 80, 50, 25)

        self.path = QLineEdit(group_path)
        self.path.setReadOnly(True)
        self.path.setStyleSheet("border:none;border-radius:8px;background-color: palette(base);")
        self.path.setGeometry(80, 80, WIDTH - 185, 25)

        path_btn = QPushButton(group_path)
        path_btn.setGeometry(self.path.x() + self.path.width() + 10, self.path.y(), 40, 25)
        path_btn.setText("...")
        path_btn.setStyleSheet("background-color: rgb(0, 99, 225); border: none; border-radius: 8px; color: white")
        path_btn.clicked.connect(self.show_dialog)

        group_data_set = QGroupBox(self)
        group_data_set.setStyleSheet(ll_ss)
        group_data_set.setTitle("Dataset settings")
        group_data_set.setGeometry(15, 155, WIDTH - 30, 280)

        lbl = QLabel(group_data_set)
        lbl.setText("Sets: ")
        lbl.setGeometry(20, 30, 50, 25)

        data_w = ["train", "validation", "test"]
        space = 15
        width = (group_data_set.width() - 100 - space * 4) / 3
        x = space + 190
        self.sets = []
        for w in data_w:
            box = QCheckBox(group_data_set)
            box.setText(w)
            box.setGeometry(x, lbl.y(), width, 25)
            box.setCheckState(2)
            x = x + space + width
            box.stateChanged.connect(self.set_check_state_changed)
            self.sets.append(box)

        lbl = QLabel(group_data_set)
        lbl.setText("EMG(Hz):")
        lbl.move(20, 80)

        self.emg_freq = QSpinBox(group_data_set)
        self.emg_freq.setMinimum(1)
        self.emg_freq.setMaximum(200)
        self.emg_freq.setValue(200)
        self.emg_freq.move(205, 79)

        lbl = QLabel(group_data_set)
        lbl.setText("IMU(Hz):")
        lbl.move(20, 130)

        self.imu_freq = QSpinBox(group_data_set)
        self.imu_freq.setMinimum(1)
        self.imu_freq.setMaximum(50)
        self.imu_freq.setValue(50)
        self.imu_freq.setGeometry(205, 131, 49, 20)

        lbl = QLabel(group_data_set)
        lbl.setText("Time(ms):")
        lbl.move(20, 180)

        self.dur = QSpinBox(group_data_set)
        self.dur.setMinimum(1)
        self.dur.setSingleStep(10)
        self.dur.setMaximum(5000)
        self.dur.setValue(3000)
        self.dur.setGeometry(200, 181, 55, 20)

        self.imu_check = QCheckBox(group_data_set)
        self.imu_check.setText("Include IMU")
        self.imu_check.setChecked(False)
        self.imu_check.move(18, 230)

        cancel_btn = QPushButton(self)
        cancel_btn.setText("Cancel")
        cancel_btn.clicked.connect(self.closeAndShowParent)
        cancel_btn.setGeometry(WIDTH - 115, group_data_set.y() + group_data_set.height() + 15, 100, 30)
        cancel_btn.setStyleSheet("background-color: red;color: white; border: none; border-radius:5px;")

        create_btn = QPushButton(self)
        create_btn.setText("Create")
        create_btn.clicked.connect(self.create_data_set)
        create_btn.setGeometry(cancel_btn.x() - 100 - 50, group_data_set.y() + group_data_set.height() + 15, 100, 30)
        create_btn.setStyleSheet("background-color: rgb(0, 99, 225);color: white; border: none; border-radius:5px;")

        self.add_gesture_txt = QLineEdit(group_data_set)
        self.add_gesture_txt.setStyleSheet("border:none;border-radius:8px;background-color: palette(base);")
        self.add_gesture_txt.setGeometry(370, 75, 160, 25)

        add_gesture_btn = QPushButton(group_data_set)
        add_gesture_btn.setGeometry(540, 75, 40, 25)
        add_gesture_btn.setText("Add")
        add_gesture_btn.setStyleSheet("background-color: rgb(0, 99, 225); border: none; border-radius: 8px; color: white")
        add_gesture_btn.clicked.connect(self.add_gesture)

        self.gestures_list = GestureListView(group_data_set)
        self.gestures_list.setStyleSheet("border: none;border-radius:8px;background-color:palette(base);")
        self.gestures_list.setGeometry(370, 125, 210, 125)

    def closeAndShowParent(self):
        self.parent().show()
        self.close()

    def add_gesture(self):
        for i in range(self.gestures_list.model().rowCount()):
            if (self.gestures_list.model().index(i).data() == self.add_gesture_txt.text()):
                return
        self.gestures_list.model().insertRow(self.gestures_list.model().rowCount())
        index = self.gestures_list.model().index(self.gestures_list.model().rowCount() - 1)
        self.gestures_list.model().setData(index, self.add_gesture_txt.text())
        self.add_gesture_txt.setText("")

    def set_check_state_changed(self):
        sum = 0
        for set in self.sets:
            if set.checkState() == 2:
                sum = sum + 1
        if sum == 0:
            self.sender().setCheckState(2)

    def show_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        dir = QFileDialog.getExistingDirectory(self, "Choose dataset destination", "/", options=options)
        if dir:
            self.path.setText(dir)

    def create_data_set(self):
        if len(self.name.text()) > 0 and len(self.path.text()):
            path = self.path.text() + "/" + self.name.text()
            dis = path + ".myo"

            os.makedirs(path)

            sets = []
            for set in self.sets:
                if set.checkState() == 2:
                    sets.append(set.text())
                    os.makedirs(path + "/" + set.text())
                    for i in range(self.gestures_list.model().rowCount()):
                        os.makedirs(path + "/" + set.text() + "/" + self.gestures_list.model().index(i).data())

            gestures = []
            for i in range(self.gestures_list.model().rowCount()):
                gestures.append(self.gestures_list.model().index(i).data())

            project = {
                "name": self.name.text(),
                "location" : path,
                "sets" : sets,
                "duration" : self.dur.value(),
                "emg_freq" : self.emg_freq.value(),
                "imu_freq" : self.imu_freq.value(),
                "imu_check" : max(0, self.imu_check.checkState() - 1),
                "gestures" : gestures,
                "last" : 0
            }

            with open(dis, 'w') as outfile:
                json.dump(project, outfile)

            self.close()
            w = MainWindow(self.parent(), dis)
            w.show()