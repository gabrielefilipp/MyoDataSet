from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from NewProjectWindow import NewProjectWindow
from MainWindow import MainWindow
from KerasWindow import KerasWindow

HEIGHT = 300
WIDTH = 450

ll_ss = "QGroupBox {border: 1px solid gray;border-radius: 9px;margin-top: 0.5em;} QGroupBox::title {subcontrol-origin: margin;left: 10px;padding: 0 3px 0 3px;}"

class ProjectWindow(QMainWindow):

    def __init__(self, parent=None):
        super(ProjectWindow, self).__init__(parent)

        #self.setupMenu()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("MyoDataset")
        self.setGeometry(240, 120, WIDTH, HEIGHT)
        self.setFixedSize(QSize(WIDTH, HEIGHT))

        img = QLabel(self)
        img.setPixmap(QPixmap("images/logo.png"))
        img.setScaledContents(True)
        img.setGeometry((WIDTH - 120) / 2, HEIGHT * 0.1, 120, 120)

        space = 30

        width = (WIDTH - space * 4) / 3

        x = space

        create_btn = QPushButton(self)
        create_btn.setText("New Dataset")
        create_btn.clicked.connect(self.create_data_set)
        create_btn.setGeometry(space, HEIGHT * 0.75, width, 40)
        create_btn.setStyleSheet("background-color: rgb(0, 99, 225);color: white; border: none; border-radius:5px;")

        x = x + space + width

        open_btn = QPushButton(self)
        open_btn.setText("Open Dataset")
        open_btn.clicked.connect(self.open_data_set)
        open_btn.setGeometry(x, HEIGHT * 0.75, width, 40)
        open_btn.setStyleSheet("background-color: rgb(120, 99, 225);color: white; border: none; border-radius:5px;")

        x = x + space + width

        open_network = QPushButton(self)
        open_network.setText("Open network")
        open_network.clicked.connect(self.open_keras_network)
        open_network.setGeometry(x, HEIGHT * 0.75, width, 40)
        open_network.setStyleSheet("background-color: rgb(220, 99, 225);color: white; border: none; border-radius:5px;")

        x = x + space + width

    def setupMenu(self):
        bar: QMenuBar = self.menuBar()

        file = bar.addMenu("File")
        create = QAction("Create Dataset", self)
        create.triggered.connect(self.create_data_set)
        file.addAction(create)

        open = QAction("Open Dataset", self)
        open.triggered.connect(self.open_data_set)
        file.addAction(open)

    def create_data_set(self):
        self.hide()
        w = NewProjectWindow(self)
        w.show()

    def open_data_set(self):
        self.hide()
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "Myo Dataset (*.myo)", options=options)
        if fileName:
            w = MainWindow(self, fileName)
            w.show()
        else:
            self.show()

    def open_keras_network(self):
        self.hide()
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "Keras model (*.h5)", options=options)
        if fileName:
            w = KerasWindow(self, fileName)
            w.show()
        else:
            self.show()