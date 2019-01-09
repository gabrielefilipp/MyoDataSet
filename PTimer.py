from PyQt5.QtCore import QTimer

class PTimer(QTimer):

    def __init__(self, parent=None, func=None):
        super().__init__(parent)
        self.duration = -1
        self.tick_count = -1
        if func:
            self.timeout.connect(func)
        self.timeout.connect(self.decrease_tick)
        self.func = None

    def setDuration(self, duration):
        self.duration = duration

    def setTickCount(self, count):
        self.tick_count = count

    def start(self, p_int=None):
        super().start(p_int)
        if self.duration > 0:
            QTimer.singleShot(self.duration, self.stop)

    def connect_to_stop(self, func):
        self.func = func

    def decrease_tick(self):
        self.tick_count = self.tick_count - 1
        if self.tick_count == 0:
            self.stop()
            if self.func:
                self.func()