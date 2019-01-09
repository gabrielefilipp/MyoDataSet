from PyQt5.QtCore import QSize, QStringListModel
from PyQt5.QtWidgets import *
from MyoManager import MyoManager, EventType
from PTimer import PTimer
from PListView import PListView
from ViewDataWindow import ViewDataWindow
import datetime
import os
from subprocess import call
import shutil
import uuid
import json

HEIGHT = 530
WIDTH = 820

#data_set_path = "/Users/gabrielefilipponi/Documents/data_set_myo"
#data_w = ["train", "validation", "test"]
#data_g = ["left", "right", "fist", "ok", "point", "scissors", "pistol", "three", "five", "rabbit"]
ll_ss = "QGroupBox {border: 1px solid gray;border-radius: 9px;margin-top: 0.5em;} QGroupBox::title {subcontrol-origin: margin;left: 10px;padding: 0 3px 0 3px;}"
ll_ss_txt = "border: 0.5px solid;border-radius:8px;background-color:palette(base);border-color: rgb(128, 128, 128);"


class MainWindow(QMainWindow):

    def __init__(self, parent=None, data_set = ""):
        super(MainWindow, self).__init__(parent)

        self.current_sum = 0
        self.emg = []
        self.imu = []
        self.myo = None
        self.check_timer = PTimer(self, self.check_sample)

        self.read_data_set(data_set)

        self.initUI()

    def read_data_set(self, data_set):
        with open(data_set) as f:
            self.project = json.load(f)

    def initUI(self):
        self.setWindowTitle(self.project["name"])

        self.setGeometry(240, 120, WIDTH, HEIGHT)
        self.setFixedSize(QSize(WIDTH, HEIGHT))

        files_group = QGroupBox(self)
        files_group.setGeometry(20, 10, 590, 300)
        files_group.setTitle("Files")
        files_group.setStyleSheet(ll_ss)

        act_group = QGroupBox(self)
        act_group.setGeometry(630, 10, 170, 300)
        act_group.setTitle("Actions")
        act_group.setStyleSheet(ll_ss)

        log_group = QGroupBox(self)
        log_group.setGeometry(20, 320, 430, 190)
        log_group.setTitle("Log")
        log_group.setStyleSheet(ll_ss)

        device_group = QGroupBox(self)
        device_group.setGeometry(470, 320, 160, 190)
        device_group.setTitle("Device")
        device_group.setStyleSheet(ll_ss)

        status_group = QGroupBox(self)
        status_group.setGeometry(650, 320, 150, 190)
        status_group.setTitle("Status")
        status_group.setStyleSheet(ll_ss)

        self.wheres = QComboBox(act_group)
        self.gestures = QComboBox(act_group)

        self.wheres.setGeometry(10, 30, 150, 25)

        for w in self.project["sets"]:
            self.wheres.addItem(w)
        self.wheres.currentIndexChanged.connect(self.refresh_list)

        self.gestures.setGeometry(10, 70, 150, 25)

        for g in self.project["gestures"]:
            self.gestures.addItem(g)
        self.gestures.currentIndexChanged.connect(self.refresh_list)

        lbl = QLabel(act_group)
        lbl.setText("EMG(Hz):")
        lbl.move(18, 111)

        self.emg_freq = QSpinBox(act_group)
        self.emg_freq.setMinimum(1)
        self.emg_freq.setMaximum(200)
        self.emg_freq.setValue(self.project["emg_freq"])
        self.emg_freq.move(act_group.width() - 65, 110)

        lbl = QLabel(act_group)
        lbl.setText("IMU(Hz):")
        lbl.move(18, 146)

        self.imu_freq = QSpinBox(act_group)
        self.imu_freq.setMinimum(1)
        self.imu_freq.setMaximum(50)
        self.imu_freq.setValue(self.project["emg_freq"])
        self.imu_freq.setGeometry(act_group.width() - 65, 145, 49, 20)

        lbl = QLabel(act_group)
        lbl.setText("Time(ms):")
        lbl.move(18, 181)

        self.dur = QSpinBox(act_group)
        self.dur.setMinimum(1)
        self.dur.setSingleStep(10)
        self.dur.setMaximum(5000)
        self.dur.setValue(self.project["duration"])
        self.dur.setGeometry(act_group.width() - 71, 181, 55, 20)

        self.imu_check = QCheckBox(act_group)
        self.imu_check.setText("Include IMU")
        self.imu_check.setChecked(self.project["imu_check"] == 1)
        self.imu_check.move(16, 215)

        self.startbtn = QPushButton(act_group)
        self.startbtn.setText("Start")
        self.startbtn.setStyleSheet("QPushButton::disabled{background-color: rgb(245, 245, 245);color: rgb(140, 140, 140); border: none; border-radius:5px;} QPushButton::enabled{background-color: rgb(0, 99, 225);color: white; border: none; border-radius:5px;}")
        self.startbtn.setGeometry(15, 250, 140, 22)
        self.startbtn.clicked.connect(self.start)
        self.startbtn.setEnabled(False)

        self.log_txt = QPlainTextEdit(log_group)
        self.log_txt.setStyleSheet(ll_ss_txt)
        self.log_txt.setGeometry(15, 25, log_group.width() - 30, log_group.height() - 40)
        self.log_txt.textChanged.connect(self.scroll_log_view)
        self.log_txt.setReadOnly(True)
        self.add_log("Application Started")

        self.dev_name = QLabel(device_group)
        self.dev_name.setText("Name: <unknown>")
        self.dev_name.setMaximumWidth(device_group.width() - 30)
        self.dev_name.move(15, 25)

        self.dev_batt = QLabel(device_group)
        self.dev_batt.setText("Battery: <unknown>")
        self.dev_batt.setMaximumWidth(device_group.width() - 30)
        self.dev_batt.move(15, 55)

        dev_con = QLabel(device_group)
        dev_con.setText("Connected: ")
        dev_con.setMaximumWidth(device_group.width() - 30)
        dev_con.move(15, 85)

        self.dev_con_color = QFrame(device_group)
        self.dev_con_color.setStyleSheet("background-color:red;border-radius:10px;")
        self.dev_con_color.setGeometry(device_group.width() - 15 - 20, 83, 20, 20)

        self.conbtn = QPushButton(device_group)
        self.conbtn.setText("Connect")
        self.conbtn.setEnabled(True)
        self.conbtn.setGeometry(10, 110, device_group.width() - 20, 25)
        self.conbtn.clicked.connect(self.connection)

        self.discbtn = QPushButton(device_group)
        self.discbtn.setText("Disconnect")
        self.discbtn.setGeometry(10, 145, device_group.width() - 20, 25)
        self.discbtn.setEnabled(False)
        self.discbtn.clicked.connect(self.disconnection)

        reclbl = QLabel(status_group)
        reclbl.setText("Recording: ")
        reclbl.setMaximumWidth(status_group.width() - 30)
        reclbl.move(15, 25)

        self.rec_con_color = QFrame(status_group)
        self.rec_con_color.setStyleSheet("background-color:red;border-radius:10px;")
        self.rec_con_color.setGeometry(status_group.width() - 15 - 20, 23, 20, 20)

        self.rec_proglbl = QLabel(status_group)
        self.rec_proglbl.setText("Progress: 0%")
        self.rec_proglbl.setMaximumWidth(status_group.width() - 30)
        self.rec_proglbl.setGeometry(15, 55, status_group.width() - 30, 25)

        self.rec_prog = QProgressBar(status_group)
        self.rec_prog.setMaximum(100)
        self.rec_prog.setGeometry(15, 90, status_group.width() - 30, 10)

        self.fileslbl = QLabel(status_group)
        self.fileslbl.setText("Files: ")
        self.fileslbl.setMaximumWidth(status_group.width() - 30)
        self.fileslbl.setGeometry(15, 110, status_group.width() - 30, 25)

        self.listview = PListView(files_group, ll_ss_txt, self.project)
        self.listview.setGeometry(15, 25, files_group.width() - 30, files_group.height() - 40)
        self.listview.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.listview.doubleClicked.connect(self.view_data)
        self.listview.contextMenuShowed.connect(self.view_data)
        self.listview.contextMenuDifferenced.connect(self.show_diff_data)
        self.listview.contextMenuAveraged.connect(self.show_ave_data)
        self.listview.contextMenuShowedFinder.connect(self.show_finder)
        self.listview.contextMenuMoved.connect(self.move_data)
        self.listview.contextMenuDeleted.connect(self.delete_data)
        self.model = QStringListModel()
        self.listview.setModel(self.model)

        self.list_data_for_set_and_gesture("train", "left")

        self.add_log("Loading dataset...")
        total = 0
        for set in self.project["sets"]:
            for gesture in self.project["gestures"]:
                path = self.project["location"] + "/" + set + "/" + gesture
                sum = 0
                for f in os.listdir(path):
                    if not f.startswith("."):
                        sum = sum + 1
                total = total + sum
                self.add_log("Found " + str(sum) + " files at " + set + "/" + gesture, False)
        self.add_log("Found " + str(total) + " files")

    def connection(self):
        if not self.myo:
            self.myo = MyoManager(sender=self)

        if not self.myo.connected:
            self.myo.connect()

    def disconnection(self):
        if self.myo:
            if self.myo.connected:
                self.myo.disconnect()

    def view_data(self):
        for index in self.listview.selectedIndexes():
            path = self.project["location"] + "/" + self.project["sets"][self.wheres.currentIndex()] + "/" + self.project["gestures"][self.gestures.currentIndex()] + "/" + index.data() + ".json"
            w = ViewDataWindow(self, [path])
            w.show()

    def show_diff_data(self):
        paths = []
        for index in self.listview.selectedIndexes():
            paths.append(self.project["location"] + "/" + self.project["sets"][self.wheres.currentIndex()] + "/" + self.project["gestures"][self.gestures.currentIndex()] + "/" + index.data() + ".json")
        w = ViewDataWindow(self, paths, 'diff')
        w.show()

    def show_ave_data(self):
        paths = []
        for index in self.listview.selectedIndexes():
            paths.append(self.project["location"] + "/" + self.project["sets"][self.wheres.currentIndex()] + "/" + self.project["gestures"][self.gestures.currentIndex()] + "/" + index.data() + ".json")
        w = ViewDataWindow(self, paths, 'ave')
        w.show()

    def show_finder(self):
        args = ["open", "-R"]
        for index in self.listview.selectedIndexes():
            args.append(self.project["location"] + "/" + self.project["sets"][self.wheres.currentIndex()] + "/" + self.project["gestures"][self.gestures.currentIndex()] + "/" + index.data() + ".json")
        call(args)

    def move_data(self, action:QAction):
        tmp = {}
        for index in self.listview.selectedIndexes():
            tmp[str(index.row())] = index.data()

        for row, data in sorted(tmp.items(), reverse=True):
            self.current_sum = self.current_sum - 1
            where = action.parent().title()
            gesture = action.text()
            src = self.project["location"] + "/" + self.project["sets"][self.wheres.currentIndex()] + "/" + self.project["gestures"][self.gestures.currentIndex()] + "/" + data + ".json"
            dest = self.project["location"] + "/" + where + "/" + gesture + "/" + data + ".json"
            shutil.copy(src, dest)
            os.remove(src)
            self.model.removeRow(int(row))
            
        self.fileslbl.setText("Files: " + str(self.current_sum))

    def delete_data(self):
        result = QMessageBox.question(
            self, 'Yes', 'Are you sure you want to delete this file',
            QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.Yes)
        if result == QMessageBox.Yes:
            tmp = {}
            for index in self.listview.selectedIndexes():
                tmp[str(index.row())] = index.data()

            for row, data in sorted(tmp.items(), reverse=True):
                self.current_sum = self.current_sum - 1
                path = self.project["location"] + "/" + self.project["sets"][self.wheres.currentIndex()] + "/" + self.project["gestures"][self.gestures.currentIndex()] + "/" + data + ".json"
                os.remove(path)
                self.model.removeRow(int(row))

            self.fileslbl.setText("Files: " + str(self.current_sum))

    def scroll_log_view(self):
        self.log_txt.verticalScrollBar().setValue(self.log_txt.document().size().height())

    def list_data_for_set_and_gesture(self, set, gesture):
        self.model.setStringList({})
        path = self.project["location"] + "/" + set + "/" + gesture
        os.chdir(path)
        files = filter(os.path.isfile, os.listdir(path))
        files = [os.path.join(path, f) for f in files]  # add path to each file
        files.sort(key=lambda x: os.path.getmtime(x))
        self.current_sum = 0
        for file in files:
            f = os.path.basename(file).replace(".json", "")
            if f.startswith("."):
                continue
            self.current_sum = self.current_sum + 1
            self.model.insertRow(self.model.rowCount())
            index = self.model.index(self.model.rowCount() - 1)
            self.model.setData(index, f)

        self.fileslbl.setText("Files: " + str(self.current_sum))

    def add_log(self, str, date = True):
        if date:
            #self.log_txt.insertHtml("<p>[" + datetime.datetime.now().strftime("%H:%M:%S") + "]: " + str + "<br></p>")
            self.log_txt.appendPlainText("[" + datetime.datetime.now().strftime("%H:%M:%S") + "]: " + str)
        else:
            #self.log_txt.insertHtml("<p>" + str + "<br></p>")
            self.log_txt.appendPlainText(str)
        #self.log_txt.repaint()

    def refresh_list(self):
        set = self.project["sets"][self.wheres.currentIndex()]
        gesture = self.project["gestures"][self.gestures.currentIndex()]
        self.list_data_for_set_and_gesture(set, gesture)

    def start(self):
        if self.startbtn.isEnabled():
            self.listview.clearFocus()
            # index = QModelIndex()
            # self.listview.setCurrentIndex(index)
            self.startbtn.setEnabled(False)
            self.start_sampling()

    def callback(self, dict):
        type = dict["type"]
        data = dict["data"]
        if type == EventType.connected:
            self.dev_con_color.setStyleSheet("background-color:green;border-radius:10px;")
            self.dev_name.setText("Name: " + repr(data["name"]))
            self.dev_batt.setText("Battery: <unknown>")
            self.conbtn.setEnabled(False)
            self.discbtn.setEnabled(True)
            self.startbtn.setEnabled(True)
        elif type == EventType.battery_level:
            self.dev_batt.setText("Battery: " + str(data["battery"]) + "%")
        elif type == EventType.disconnected:
            self.dev_con_color.setStyleSheet("background-color:red;border-radius:10px;")
            self.dev_name.setText("Name: <unknown>")
            self.dev_batt.setText("Battery: <unknown>")
            self.conbtn.setEnabled(True)
            self.discbtn.setEnabled(False)
            self.startbtn.setEnabled(False)

        self.repaint()

    def start_sampling(self):
        self.add_log("Started sampling data")
        self.rec_con_color.setStyleSheet("background-color:green;border-radius:10px;")

        self.rec_con_color.repaint()

        self.emg.clear()
        self.imu.clear()

        duration = self.dur.value() / 1000

        emg_timer = PTimer(self, self.sample_emg)
        emg_timer.setTickCount(int(duration * self.emg_freq.value()))
        emg_timer.start(1000 / self.emg_freq.value())


        if self.imu_check.isChecked():
            imu_timer = PTimer(self, self.sample_imu)
            imu_timer.setTickCount(int(duration * self.imu_freq.value()))
            imu_timer.start(1000 / self.imu_freq.value())

        self.check_timer.start(100)

    def check_sample(self):
        duration = self.dur.value() / 1000
        emg_ended = len(self.emg) == duration * self.emg_freq.value()
        imu_ended = (len(self.imu) == duration * self.imu_freq.value())
        if emg_ended and (not self.imu_check.isChecked() or (self.imu_check.isChecked() and imu_ended)):
            self.sample_ended()
            self.check_timer.stop()

    def sample_emg(self):
        self.emg.append(self.myo.listener.emg)
        perc = int(len(self.emg) * 100 / (self.dur.value() / 1000 * self.emg_freq.value()))
        self.rec_proglbl.setText("Progress: " + str(perc) + "%")
        self.rec_prog.setValue(perc)

    def sample_imu(self):
        self.imu.append(self.myo.listener.data)

    def sample_ended(self):
        self.rec_con_color.setStyleSheet("background-color:red;border-radius:10px;")

        self.rec_con_color.repaint()

        self.add_log("Sampled ended")
        self.add_log("Saving data")

        name = str(uuid.uuid4())
        path = self.project["location"] + "/" + self.project["sets"][self.wheres.currentIndex()] + "/" + self.project["gestures"][self.gestures.currentIndex()] + "/" + name + ".json"

        data = {
            "date" : datetime.datetime.now().strftime("%d/%m/%y/%H:%M:%S"),
            "duration" : self.dur.value(),
            "emg" : {
                "frequency" : self.emg_freq.value(),
                "data" : self.emg
            }
        }

        if self.imu_check.isChecked():
            data["imu"] = {
                "frequency": self.imu_freq.value(),
                "data": self.imu
            }

        with open(path, 'w') as outfile:
            json.dump(data, outfile)

        self.add_log("Data saved")

        self.model.insertRow(self.model.rowCount())
        index = self.model.index(self.model.rowCount() - 1)
        self.model.setData(index, name)

        self.startbtn.setEnabled(True)

        self.current_sum = self.current_sum + 1
        self.fileslbl.setText("Files: " + str(self.current_sum))

    def keyPressEvent(self, event):
        if event.key() == 16777216:
            self.disconnection()
        elif event.key() == 16777220:
            if not self.listview.hasFocus() or len(self.listview.selectedIndexes()) == 0:
                if self.myo:
                    if self.myo.connected:
                        self.start()

    def closeEvent(self, QCloseEvent):
        self.parent().show()
        self.disconnection()