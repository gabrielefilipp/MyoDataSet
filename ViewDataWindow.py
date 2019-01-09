from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import *
from MultiGraphWidget import MultiGraphWidget
import json
import math

import pywt

import featuringObj

import numpy as np

HEIGHT = 600
WIDTH = 1080

ll_ss = "QGroupBox {border: 1px solid gray;border-radius: 9px;margin-top: 0.5em;} QGroupBox::title {subcontrol-origin: margin;left: 10px;padding: 0 3px 0 3px;}"

class ViewDataWindow(QMainWindow):

    def __init__(self, parent=None, paths = [], mode='show'):
        super().__init__(parent)

        self.emgGraphs = []

        self.read_data_files(paths, mode)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("ViewData")
        self.setGeometry(240, 120, WIDTH, HEIGHT)
        self.setFixedSize(QSize(WIDTH, HEIGHT))

        self.stacked = QStackedWidget(self)
        self.stacked.setStyleSheet("QStackedWidget{background-color:white; border-radius:10px}")
        self.stacked.setGeometry(10, 35, WIDTH - 20, HEIGHT - 45)

        self.graph_page = QWidget()
        self.graph_page.setGeometry(0, 0, self.stacked.width(), self.stacked.height())
        self.setup_graph_page()

        self.raw_page = QWidget()
        self.raw_page.setGeometry(0, 0, self.stacked.width(), self.stacked.height())
        self.setup_raw_page()

        self.features_page = QWidget()
        self.features_page.setGeometry(0, 0, self.stacked.width(), self.stacked.height())
        self.setup_features_page()

        self.features_plot_page = QWidget()
        self.features_plot_page.setGeometry(0, 0, self.stacked.width(), self.stacked.height())
        self.setup_features_plot_page()

        self.stacked.addWidget(self.graph_page)
        self.stacked.addWidget(self.features_page)
        self.stacked.addWidget(self.features_plot_page)
        self.stacked.addWidget(self.raw_page)

        self.stacked.setCurrentIndex(0)

        btn_w = 100
        btn_h = 25

        btn_x = (WIDTH - btn_w * 4) / 2

        self.graph_btn = QPushButton(self)
        self.graph_btn.setText("Graphs")
        self.graph_btn.setStyleSheet("background-color:white; border-top: solid;")
        self.graph_btn.setGeometry(btn_x, 10, btn_w, btn_h)
        self.graph_btn.clicked.connect(self.change_to_graph)

        btn_x = btn_x + btn_w

        self.features_btn = QPushButton(self)
        self.features_btn.setText("Features")
        self.features_btn.setStyleSheet("background-color: rgb(220, 220, 220); border-top: solid;")
        self.features_btn.setGeometry(btn_x, 10, btn_w, btn_h)
        self.features_btn.clicked.connect(self.change_to_features)

        btn_x = btn_x + btn_w

        self.features_plot_btn = QPushButton(self)
        self.features_plot_btn.setText("Plot features")
        self.features_plot_btn.setStyleSheet("background-color: rgb(220, 220, 220); border-top: solid;")
        self.features_plot_btn.setGeometry(btn_x, 10, btn_w, btn_h)
        self.features_plot_btn.clicked.connect(self.change_to_features_plot)

        btn_x = btn_x + btn_w

        self.raw_btn = QPushButton(self)
        self.raw_btn.setText("Raw")
        self.raw_btn.setStyleSheet("background-color: rgb(220, 220, 220); border-top: solid;")
        self.raw_btn.setGeometry(btn_x, 10, btn_w, btn_h)
        self.raw_btn.clicked.connect(self.change_to_raw)

        btn_x = btn_x + btn_w

    def read_data_files(self, paths, mode):
        tmp = None
        emg = []
        flag = True
        for path in paths:
            with open(path) as f:
                tmp = json.load(f)
            if flag:
                flag = False
                #emg = tmp["emg"]["data"]
                dim = int(tmp["duration"] / 1000) * int(tmp["emg"]["frequency"])
                for i in range(dim):
                    emg.append([])
                    for l in range(8):
                        emg[i].append(tmp["emg"]["data"][i][l])
                #TODO: Add imu
            else:
                if mode == 'diff':
                    for i in range(len(emg)):
                        for l in range(8):
                            emg[i][l] = emg[i][l] - tmp["emg"]["data"][i][l]
                elif mode == 'ave':
                    for i in range(len(emg)):
                        for l in range(8):
                            emg[i][l] = emg[i][l] + tmp["emg"]["data"][i][l]
        if mode == 'ave':
            for i in range(len(emg)):
                for l in range(8):
                    emg[i][l] = emg[i][l] / len(paths)
        tmp["emg"]["data"] = emg
        self.data = tmp

    def setup_raw_page(self):
        self.raw = QTextBrowser(self.raw_page)
        self.raw.setStyleSheet("border-radius: 6px; background-color: rgb(240, 240, 240); border: solid 1px black;")
        self.raw.setGeometry(10, 10, self.raw_page.width() - 20, self.raw_page.height() - 20)

        self.raw.setPlainText(json.dumps(self.data, indent=20, sort_keys=False))

    # def hampel(self, vals_orig, k=7, t0=3):
    #     '''
    #     vals: pandas series of values from which to remove outliers
    #     k: size of window (including the sample; 7 is equal to 3 on either side of value)
    #     '''
    #
    #     # Make copy so original not edited
    #     vals = vals_orig.copy()
    #
    #     # Hampel Filter
    #     L = 1.4826
    #     rolling_median = vals.rolling(window=k, center=True).median()
    #     MAD = lambda x: np.median(np.abs(x - np.median(x)))
    #     rolling_MAD = vals.rolling(window=k, center=True).apply(MAD)
    #     threshold = t0 * L * rolling_MAD
    #     difference = np.abs(vals - rolling_median)
    #
    #     '''
    #     Perhaps a condition should be added here in the case that the threshold value
    #     is 0.0; maybe do not mark as outlier. MAD may be 0.0 without the original values
    #     being equal. See differences between MAD vs SDV.
    #     '''
    #
    #     outlier_idx = difference > threshold
    #     vals[outlier_idx] = np.nan
    #     return (vals)

    # def HampelFilter(self, wk, K, FilterParms):
    #     """
    #     Procedure to implement the Hampel filter
    #     """
    #     #
    #     Thresh = FilterParms[0]
    #     ctr = wk[K]
    #     ref = self.MedianFunction(wk)
    #     AbsDev = [abs(r - ref) for r in wk]
    #     MAD = 1.4826 * self.MedianFunction(AbsDev)
    #     TestVal = abs(ctr - ref)
    #     if TestVal > Thresh * MAD:
    #         yk = ref
    #     else:
    #         yk = ctr
    #     return yk

    def hamperlFilter(self, data, k=7, t=3):
        tmp = data.copy()
        window = 0
        for i in range(0, len(data) - k*2):
            if window < k*2 + 1:
                window = window + 1
            sub_data = data[i:i + window]

            m = np.median(sub_data)
            MADM = 1.4826 * np.median(abs(sub_data - m))

            if abs(sub_data[int(window / 2)] - m) > t*MADM:
                tmp[i + k] = m
        return tmp


    def setup_graph_page(self):
        dim_emg = int(self.data["duration"]) / 1000 * int(self.data["emg"]["frequency"])

        for i in range(8):
            if i==0:
                color=(255, 0, 0)
            elif i==1:
                color=(255, 165, 0)
            elif i==2:
                color=(255, 210, 0)
            elif i==3:
                color=(0, 128, 0)
            elif i==4:
                color=(0, 255, 255)
            elif i==5:
                color=(0, 0, 255)
            elif i==6:
                color=(255, 0, 255)
            elif i==7:
                color=(205, 133, 63)

            g = MultiGraphWidget(self.graph_page, max_data=dim_emg, y_range=150, channels=2, colors=[color, (0, 0, 0, 255)], background="w", title="<b>Pod " + repr(i + 1) + "</b>")

            emg = self.data["emg"]["data"]

            array = []
            for sample in emg:
                if len(sample) > i:
                    array.append(sample[i])

            if False:
                # Set a target SNR
                target_snr_db = 25
                # Calculate signal power and convert to dB
                sig_avg_watts = np.mean(np.asarray(array) ** 2)
                sig_avg_db = 10 * np.log10(sig_avg_watts)
                # Calculate noise according to [2] then convert to watts
                noise_avg_db = sig_avg_db - target_snr_db
                noise_avg_watts = 10 ** (noise_avg_db / 10)
                # Generate an sample of white noise
                mean_noise = 0
                noise_volts = np.random.normal(mean_noise, noise_avg_watts, len(array))
                # Noise up the original signal
                array = array + noise_volts

            g.set_data_to_channel(np.asarray(array), 0)
            #g.set_data_to_channel(self.hamperlFilter(np.asarray(array)), 1)

            self.emgGraphs.append(g)



        tmp = self.emgGraphs

        if ("imu" in self.data):
            dim_imu = int(self.data["duration"]) / 1000 * int(self.data["imu"]["frequency"])

            self.gyroGraph = MultiGraphWidget(self.graph_page, max_data=dim_imu, y_range=1000, background="w", channels=3,
                                          title="<b>Gyroscope</b>")

            imu = self.data["imu"]["data"]

            x = []
            y = []
            z = []
            for d in imu:
                sample = d["gyroscope"]
                if len(sample) == 3:
                    x.append(sample[0])
                    y.append(sample[1])
                    z.append(sample[2])
            self.gyroGraph.set_data_to_channel(x, 0)
            self.gyroGraph.set_data_to_channel(y, 1)
            self.gyroGraph.set_data_to_channel(z, 2)

            self.accGraph = MultiGraphWidget(self.graph_page, max_data=dim_imu, y_range=3, background="w", channels=3,
                                         title="<b>Acceleration</b>")

            x.clear()
            y.clear()
            z.clear()
            for d in imu:
                sample = d["acceleration"]
                if len(sample) == 3:
                    x.append(sample[0])
                    y.append(sample[1])
                    z.append(sample[2])
            self.accGraph.set_data_to_channel(x, 0)
            self.accGraph.set_data_to_channel(y, 1)
            self.accGraph.set_data_to_channel(z, 2)

            self.orienGraph = MultiGraphWidget(self.graph_page, max_data=dim_imu, y_range=1, background="w", channels=4,
                                               title="<b>Orientation</b>")

            x.clear()
            y.clear()
            z.clear()
            w = []
            for d in imu:
                sample = d["orientation"]
                if len(sample) == 4:
                    x.append(sample[0])
                    y.append(sample[1])
                    z.append(sample[2])
                    w.append(sample[3])
            self.orienGraph.set_data_to_channel(x, 0)
            self.orienGraph.set_data_to_channel(y, 1)
            self.orienGraph.set_data_to_channel(z, 2)
            self.orienGraph.set_data_to_channel(w, 3)

            tmp = tmp + [self.gyroGraph, self.orienGraph, self.accGraph]

        size: QSize = self.graph_page.size()

        le = len(tmp)

        in_w = 3

        in_h = math.ceil(le / in_w)

        space = 10

        x = space
        y = space
        h = (size.height() - ((in_h + 1) * space)) / in_h
        w = (size.width() - ((in_w + 1) * space)) / in_w

        for i in range(len(tmp)):
            g: QWidget = tmp[i]
            g.setGeometry(x, y, w, h)
            if (i + 1) % in_w == 0:
                x = space
                y = y + h + space
            else:
                x = x + space + w

    def setup_features_page(self):
        space = 10

        self.wft = []

        self.feature_pod = QComboBox(self.features_page)
        self.feature_pod.addItem("Select Pod")
        for i in range(8):
            self.feature_pod.addItem("Pod " + str(i + 1))
        self.feature_pod.currentIndexChanged.connect(self.calculate_features)

        self.db_box = QComboBox(self.features_page)
        for i in range(7):
            self.db_box.addItem("dB" + str(i + 1))
        self.db_box.setCurrentIndex(6)
        self.db_box.currentIndexChanged.connect(self.calculate_features)

        self.feature_pod.setGeometry((self.features_page.width() - 150) / 2 - 75, 10, 150, 25)
        self.db_box.setGeometry((self.features_page.width() - 150) / 2 + 75, 10, 150, 25)


        x = space
        y = space + 35
        w = (self.features_page.width() - space * 6) / 5
        h = (self.features_page.height() - space * 3 - 35) / 2
        lbl_w = w - space * 2
        lbl_h = (h - space * 6 - 10) / 5
        names = ["cD1", "cD2", "cD3", "cD4", "cA4", "D1", "D2", "D3", "D4", "A4"]
        features = ["MAV", "RMSA", "WL", "ZC", "SSC"]
        for i in range(len(names)):
            group = QGroupBox(self.features_page)
            group.setTitle(names[i])
            group.setStyleSheet(ll_ss)
            group.setGeometry(x, y, w, h)
            if i == 4:
                x = space
                y = y + h + space
            else:
                x = x + w + space

            lbl_y = space + 10

            self.wft.append([])

            for feature in features:
                label = QLabel(group)
                label.setText(feature + ": ")
                label.setGeometry(space, lbl_y, lbl_w, lbl_h)
                lbl_y = lbl_y + lbl_h + space

                self.wft[i].append({"label" : label, "txt" : label.text()})

    def calculate_features(self):
        array = []
        emg = self.data["emg"]["data"]
        i = self.feature_pod.currentIndex() - 1
        if i == -1:
            for i in range(10):
                for f in range(5):
                    dict = self.wft[i][f]
                    label = dict["label"]
                    txt = dict["txt"]
                    label.setText(txt)
            return


        for sample in emg:
            if len(sample) > i:
                array.append(sample[i])

        wv = self.db_box.currentText()

        cA1, cD1 = pywt.dwt(array, wv)
        cA2, cD2 = pywt.dwt(cA1, wv)
        cA3, cD3 = pywt.dwt(cA2, wv)
        cA4, cD4 = pywt.dwt(cA3, wv)

        A4 = pywt.idwt(pywt.idwt(pywt.idwt(pywt.idwt(cA4, None, wv), None, wv), None, wv), None, wv)
        D4 = pywt.idwt(pywt.idwt(pywt.idwt(pywt.idwt(None, cD4, wv), None, wv), None, wv), None, wv)
        D3 = pywt.idwt(pywt.idwt(pywt.idwt(None, cD3, wv), None, wv), None, wv)
        D2 = pywt.idwt(pywt.idwt(None, cD2, wv), None, wv)
        D1 = pywt.idwt(None, cD1, wv)

        dis = [cD1, cD2, cD3, cD4, cA4, D1, D2, D3, D4, A4]

        for i in range(len(dis)):
            obj = featuringObj.featuringObj()
            features = obj.calculateAll(dis[i])
            for f in range(len(features)):
                dict = self.wft[i][f]
                label = dict["label"]
                txt = dict["txt"] + str(features[f])
                label.setText(txt)

    def setup_features_plot_page(self):
        space = 10

        self.graphs = []

        self.feature_plot_pod = QComboBox(self.features_plot_page)
        self.feature_plot_pod.addItem("Select Pod")
        for i in range(8):
            self.feature_plot_pod.addItem("Pod " + str(i + 1))
        self.feature_plot_pod.currentIndexChanged.connect(self.calculate_features_plot)

        self.db_plot_box = QComboBox(self.features_plot_page)
        for i in range(7):
            self.db_plot_box.addItem("dB" + str(i + 1))

        self.db_plot_box.setCurrentIndex(6)
        self.db_plot_box.currentIndexChanged.connect(self.calculate_features_plot)

        self.wave_box = QComboBox(self.features_plot_page)
        self.wave_box.addItem("Raw")
        waves = ["cD1", "cD2", "cD3", "cD4", "cA4", "D1", "D2", "D3", "D4", "A4"]
        for wave in waves:
            self.wave_box.addItem(wave)
        self.wave_box.currentIndexChanged.connect(self.calculate_features_plot)

        box_x = (self.features_plot_page.width() - 450) / 2
        self.feature_plot_pod.setGeometry(box_x, 10, 150, 25)
        box_x = box_x + 150
        self.db_plot_box.setGeometry(box_x, 10, 150, 25)
        box_x = box_x + 150
        self.wave_box.setGeometry(box_x, 10, 150, 25)
        box_x = box_x + 150

        x = space
        y = space + 35
        w = (self.features_page.width() - space * 4) / 3
        h = (self.features_page.height() - space * 3 - 35) / 2
        features = ["Original", "MAV", "RMSA", "WL", "ZC", "SSC"]

        dim_emg = int(self.data["duration"]) / 1000 * int(self.data["emg"]["frequency"])
        for i in range(len(features)):
            if i==0:
                color=(255, 0, 0)
            elif i==1:
                color=(255, 165, 0)
            elif i==2:
                color=(255, 210, 0)
            elif i==3:
                color=(0, 128, 0)
            elif i==4:
                color=(0, 255, 255)
            elif i==5:
                color=(0, 0, 255)
            elif i==6:
                color=(255, 0, 255)
            elif i==7:
                color=(205, 133, 63)

            g = MultiGraphWidget(self.features_plot_page, max_data=dim_emg, y_range=100, channels=1, colors=[color], background="w", title="<b>" + features[i] + "</b>")
            g.setGeometry(x, y, w, h)
            if i == 2:
                x = space
                y = y + h + space
            else:
                x = x + space + w
            self.graphs.append(g)

    def calculate_features_plot(self):
        array = []
        emg = self.data["emg"]["data"]
        i = self.feature_plot_pod.currentIndex() - 1
        if i == -1:
            for g in self.graphs:
               g.set_data_to_channel([])
            return


        for sample in emg:
            if len(sample) > i:
                array.append(sample[i])

        wv = self.db_plot_box.currentText()

        wave = self.wave_box.currentText()


        if wave == "Raw":
            self.calculate_features_plot_finally(array)
        elif wave == "cD1":
            cA1, cD1 = pywt.dwt(array, wv)
            self.calculate_features_plot_finally(cD1)
        elif wave == "cD2":
            cA1, cD1 = pywt.dwt(array, wv)
            cA2, cD2 = pywt.dwt(cD1, wv)
            self.calculate_features_plot_finally(cD2)
        elif wave == "cD3":
            cA1, cD1 = pywt.dwt(array, wv)
            cA2, cD2 = pywt.dwt(cD1, wv)
            cA3, cD3 = pywt.dwt(cD2, wv)
            self.calculate_features_plot_finally(cD3)
        elif wave == "cD4":
            cA1, cD1 = pywt.dwt(array, wv)
            cA2, cD2 = pywt.dwt(cD1, wv)
            cA3, cD3 = pywt.dwt(cD2, wv)
            cA4, cD4 = pywt.dwt(cD3, wv)
            self.calculate_features_plot_finally(cD4)
        elif wave == "cA4":
            cA1, cD1 = pywt.dwt(array, wv)
            cA2, cD2 = pywt.dwt(cD1, wv)
            cA3, cD3 = pywt.dwt(cD2, wv)
            cA4, cD4 = pywt.dwt(cD3, wv)
            self.calculate_features_plot_finally(cA4)
        elif wave == "A4":
            cA1, cD1 = pywt.dwt(array, wv)
            cA2, cD2 = pywt.dwt(cD1, wv)
            cA3, cD3 = pywt.dwt(cD2, wv)
            cA4, cD4 = pywt.dwt(cD3, wv)

            A4 = pywt.idwt(pywt.idwt(pywt.idwt(pywt.idwt(cA4, None, wv), None, wv), None, wv), None, wv)

            self.calculate_features_plot_finally(A4)
        elif wave == "D4":
            cA1, cD1 = pywt.dwt(array, wv)
            cA2, cD2 = pywt.dwt(cD1, wv)
            cA3, cD3 = pywt.dwt(cD2, wv)
            cA4, cD4 = pywt.dwt(cD3, wv)

            D4 = pywt.idwt(pywt.idwt(pywt.idwt(pywt.idwt(None, cD4, wv), None, wv), None, wv), None, wv)

            self.calculate_features_plot_finally(D4)
        elif wave == "D3":
            cA1, cD1 = pywt.dwt(array, wv)
            cA2, cD2 = pywt.dwt(cD1, wv)
            cA3, cD3 = pywt.dwt(cD2, wv)

            D3 = pywt.idwt(pywt.idwt(pywt.idwt(None, cD3, wv), None, wv), None, wv)

            self.calculate_features_plot_finally(D3)
        elif wave == "D2":
            cA1, cD1 = pywt.dwt(array, wv)
            cA2, cD2 = pywt.dwt(cD1, wv)

            D2 = pywt.idwt(pywt.idwt(None, cD2, wv), None, wv)

            self.calculate_features_plot_finally(D2)
        elif wave == "D1":
            cA1, cD1 = pywt.dwt(array, wv)
            D1 = pywt.idwt(None, cD1, wv)

            self.calculate_features_plot_finally(D1)

    def calculate_features_plot_finally(self, data):
        features = [[]]
        features[0] = data
        obj = featuringObj.featuringObj()
        for i in range(1, len(data)):
            tmp = obj.calculateAll(data[:i])
            for g in range(1, len(tmp) + 1):
                if len(features) <= g:
                    features.append([])
                features[g].append(tmp[g - 1])

        for g in range(len(features)):
            self.graphs[g].set_data_to_channel(features[g])
            self.graphs[g].setXRange(0, len(features[g]))
            self.graphs[g].setYRange(min(0, min(features[g])), max(features[g]))

    def change_to_graph(self):
        self.graph_btn.setStyleSheet("background-color:white; border-top: solid;")
        self.raw_btn.setStyleSheet("background-color: rgb(220, 220, 220); border-top: solid;")
        self.features_btn.setStyleSheet("background-color: rgb(220, 220, 220); border-top: solid;")
        self.features_plot_btn.setStyleSheet("background-color: rgb(220, 220, 220); border-top: solid;")
        self.stacked.setCurrentIndex(0)

        #self.stacked.repaint()

    def change_to_raw(self):
        self.raw_btn.setStyleSheet("background-color:white; border-top: solid;")
        self.graph_btn.setStyleSheet("background-color: rgb(220, 220, 220); border-top: solid;")
        self.features_btn.setStyleSheet("background-color: rgb(220, 220, 220); border-top: solid;")
        self.features_plot_btn.setStyleSheet("background-color: rgb(220, 220, 220); border-top: solid;")
        self.stacked.setCurrentIndex(3)
        #self.stacked.repaint()

    def change_to_features(self):
        self.features_btn.setStyleSheet("background-color:white; border-top: solid;")
        self.graph_btn.setStyleSheet("background-color: rgb(220, 220, 220); border-top: solid;")
        self.raw_btn.setStyleSheet("background-color: rgb(220, 220, 220); border-top: solid;")
        self.features_plot_btn.setStyleSheet("background-color: rgb(220, 220, 220); border-top: solid;")
        self.stacked.setCurrentIndex(1)

    def change_to_features_plot(self):
        self.features_plot_btn.setStyleSheet("background-color:white; border-top: solid;")
        self.features_btn.setStyleSheet("background-color: rgb(220, 220, 220); border-top: solid;")
        self.graph_btn.setStyleSheet("background-color: rgb(220, 220, 220); border-top: solid;")
        self.raw_btn.setStyleSheet("background-color: rgb(220, 220, 220); border-top: solid;")
        self.stacked.setCurrentIndex(2)

    def keyPressEvent(self, event):
        if event.key() == 16777216:
            self.close()