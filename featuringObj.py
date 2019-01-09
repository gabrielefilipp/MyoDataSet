from PyQt5.QtCore import QObject

import numpy as np
import math

class featuringObj(QObject):

    def __init__(self, parent = None):
        super().__init__(parent)

    def MAV(self, obj):
        return 1/len(obj)*np.sum(np.abs(obj))

    def RMS(self, obj):
        return math.sqrt(1/len(obj)*np.sum(np.power(obj, 2)))

    def WL(self, obj):
        return np.sum(np.abs(np.diff(obj)))

    def ZC(self, obj):
        return len(np.where(np.diff(np.sign(obj)))[0])

    def SSC(self, obj):
        return np.count_nonzero(np.diff(np.sign(np.diff(obj))))

    def calculateAll(self, obj):
        return [self.MAV(obj), self.RMS(obj), self.WL(obj), self.ZC(obj), self.SSC(obj)]