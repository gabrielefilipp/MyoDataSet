from PyQt5.QtCore import QSize, QStringListModel
from PyQt5.QtWidgets import *
from MyoManager import MyoManager, EventType
from PTimer import PTimer
import datetime
import numpy as np

from keras.models import load_model

HEIGHT = 520
WIDTH = 560

ll_ss = "QGroupBox {border: 1px solid gray;border-radius: 9px;margin-top: 0.5em;} QGroupBox::title {subcontrol-origin: margin;left: 10px;padding: 0 3px 0 3px;}"
ll_ss_txt = "border: 0.5px solid;border-radius:8px;background-color:palette(base);border-color: rgb(128, 128, 128);"

gestures_json = ["right", "ok", "pistol", "point", "left", "three", "rabbit", "scissors", "fist", "five"]
gestures_csv = ["fist", "five", "left", "ok", "pistol", "point", "rabbit", "right", "scissors", "three"]

class KerasWindow(QMainWindow):

    def __init__(self, parent=None, keras_model=""):
        super(KerasWindow, self).__init__(parent)

        self.current_sum = 0
        self.emg = []
        self.myo = None
        self.check_timer = PTimer(self, self.check_sample)

        self.initUI()

        self.classificator = load_model(keras_model)

    def initUI(self):
        self.setWindowTitle("Classificator")

        self.setGeometry(240, 120, WIDTH, HEIGHT)
        self.setFixedSize(QSize(WIDTH, HEIGHT))

        device_group = QGroupBox(self)
        device_group.setGeometry(20, 10, 160, 190)
        device_group.setTitle("Device")
        device_group.setStyleSheet(ll_ss)

        act_group = QGroupBox(self)
        act_group.setGeometry(200, 10, 170, 190)
        act_group.setTitle("Actions")
        act_group.setStyleSheet(ll_ss)

        status_group = QGroupBox(self)
        status_group.setGeometry(390, 10, 150, 190)
        status_group.setTitle("Status")
        status_group.setStyleSheet(ll_ss)

        gesture_group = QGroupBox(self)
        gesture_group.setGeometry(20, 210, 520, 290)
        gesture_group.setTitle("Prediction")
        gesture_group.setStyleSheet(ll_ss)

        lbl = QLabel(act_group)
        lbl.setText("EMG(Hz):")
        lbl.move(18, 25)

        self.emg_freq = QSpinBox(act_group)
        self.emg_freq.setMinimum(1)
        self.emg_freq.setMaximum(200)
        self.emg_freq.setValue(200)
        self.emg_freq.move(act_group.width() - 65, 25)

        lbl = QLabel(act_group)
        lbl.setText("Time(ms):")
        lbl.move(18, 55)

        self.dur = QSpinBox(act_group)
        self.dur.setMinimum(1)
        self.dur.setSingleStep(10)
        self.dur.setMaximum(5000)
        self.dur.setValue(3000)
        self.dur.setGeometry(act_group.width() - 71, 55, 55, 25)

        self.startbtn = QPushButton(act_group)
        self.startbtn.setText("Start")
        self.startbtn.setGeometry(10, 85, 150, 25)
        self.startbtn.clicked.connect(self.start)
        self.startbtn.setEnabled(False)

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

        x = 15
        y = 30
        self.prediction_bars = []
        for g in gestures_csv:
            lbl = QLabel(gesture_group)
            lbl.setText(g + ":")
            lbl.setGeometry(x, y, 100, 25)

            progress = QProgressBar(gesture_group)
            progress.setMaximum(100)
            progress.setGeometry(100, y + 10, gesture_group.width() - 140, 10)

            self.prediction_bars.append(progress)

            y = y + 25

    def connection(self):
        if not self.myo:
            self.myo = MyoManager(sender=self)

        if not self.myo.connected:
            self.myo.connect()

    def disconnection(self):
        if self.myo:
            if self.myo.connected:
                self.myo.disconnect()

    def refresh_list(self):
        set = self.project["sets"][self.wheres.currentIndex()]
        gesture = self.project["gestures"][self.gestures.currentIndex()]
        self.list_data_for_set_and_gesture(set, gesture)

    def start(self):
        if self.startbtn.isEnabled():
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
        self.rec_con_color.setStyleSheet("background-color:green;border-radius:10px;")

        self.rec_con_color.repaint()

        self.emg.clear()

        duration = self.dur.value() / 1000

        emg_timer = PTimer(self, self.sample_emg)
        emg_timer.setTickCount(int(duration * self.emg_freq.value()))
        emg_timer.start(1000 / self.emg_freq.value())

        self.check_timer.start(100)

    def check_sample(self):
        duration = self.dur.value() / 1000
        emg_ended = len(self.emg) == duration * self.emg_freq.value()
        if emg_ended:
            self.sample_ended()
            self.check_timer.stop()

    def sample_emg(self):
        self.emg.append(self.myo.listener.emg)
        perc = int(len(self.emg) * 100 / (self.dur.value() / 1000 * self.emg_freq.value()))
        self.rec_proglbl.setText("Progress: " + str(perc) + "%")
        self.rec_prog.setValue(perc)

    def add_log(self, str = "", flag = False):
        pass

    def sample_ended(self):
        self.rec_con_color.setStyleSheet("background-color:red;border-radius:10px;")

        self.rec_con_color.repaint()

        x = []
        for p in range(8):
            for i in range(600):
                x.append(self.emg[i][p])

        x = np.reshape(x, [1, 600, 8])

        prediction = self.classificator.predict(x)

        for i in range(10):
            self.prediction_bars[i].setValue(prediction[0, i] * 100)

        index = np.argmax(prediction)

        #self.add_log("Predicted: " + gestures_csv[index] + ' with ' + format(prediction[0, index] * 100, '.2f') + '%')
        #self.add_log("Full list: ")
        #dim = 20
        #for i in range(10):
        #    perc = prediction[0, i]
        #    self.add_log(gestures_csv[i] + ": " + " " * (max - len(gestures_csv[i])) + "*" * int(dim * perc), False)

        self.startbtn.setEnabled(True)

    def closeEvent(self, QCloseEvent):
        self.parent().show()
        self.disconnection()