from pyqtgraph import PlotWidget, mkPen, AxisItem, LabelItem, PlotDataItem
import numpy as np
import PyQt5.QtCore
from PyQt5.QtCore import *
from PyQt5.Qt import QWidget

class MultiGraphWidget(PlotWidget):

    @property
    def max_data_points(self):
        return self._max_data_points

    @max_data_points.setter
    def max_data_points(self, value):
        self._max_data_points = value
        self.setXRange(0, value)

    def __init__(self, parent=None, max_data=50, background="w", y_range=10, y_neg=True, channels=1, colors=["b", "g", "r", (0, 0, 0, 255)], **kargs):
        super().__init__(parent, background=background, **kargs)
        self._max_data_points = max_data
        self.setXRange(0, max_data)
        self.maxed = False
        if y_neg:
            self.setYRange(-y_range, y_range)
        else:
            self.setYRange(0, y_range)

        self.counter = 0

        self.setAntialiasing(False)

        self.plots = []
        self.channels = []

        self.getPlotItem().layout.setContentsMargins(0, 0, 0, 10)

        for i in range(channels):
            self.channels.append([])
            self.plots.append(self.getPlotItem().plot(pen=mkPen(width=2, color=colors[i])))

        self.getPlotItem().getAxis('bottom').setGrid(255)
        #self.getPlotItem().getAxis('bottom').setStyle(showValues = False)
        self.getPlotItem().getAxis('left').setGrid(255)

    def set_data_to_channel(self, data, channel = 0):
        self.plots[channel].setData(data)

    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        self.maxed = not self.maxed
        if self.maxed:
            self.original = self.geometry()
            parent:QWidget = self.parent()
            self.setGeometry(10, 10, parent.width() - 20, parent.height() - 20)
            self.raise_()
        else:
            self.setGeometry(self.original)