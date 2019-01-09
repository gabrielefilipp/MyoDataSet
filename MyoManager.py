import myo
from myo import *
import time
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, QCoreApplication

class Listener(myo.DeviceListener):

    def __init__(self, m):
        super().__init__();
        self.manager = m;
        self.emg = []
        self.data = {}

    def on_connected(self, event:Event):
        self.manager.connecting = False
        self.manager.connected = True
        event.device.stream_emg(True)
        event.device.request_battery_level()
        self.manager.send.add_log("Connected to " + repr(event.device_name) + " with mac address: " + repr(event.mac_address))
        event.device.vibrate(myo.VibrationType.short)
        self.manager.signals.emit({"type": event.type, "data": {"name": event.device_name, "mac_address": event.mac_address, "firmware_version": event.firmware_version}})

    def on_disconnected(self, event:Event):
        self.manager.signals.emit({"type": event.type, "data": {}})
        self.manager.connected = False

    def on_emg(self, event:Event):
        self.emg = event.emg

    def on_orientation(self, event:Event):
        self.data = {"gyroscope": [event.gyroscope.x, event.gyroscope.y, event.gyroscope.z], "acceleration": [event.acceleration.x, event.acceleration.y, event.acceleration.z], "orientation": [event.orientation.x, event.orientation.y, event.orientation.z, event.orientation.w]}

    def on_battery_level(self, event):
        self.manager.signals.emit({"type": EventType.battery_level, "data": {"battery" : event.battery_level}})

class MyoManager(QThread):

    signals = pyqtSignal(dict)
    send = None
    connecting = False
    connected = False

    def __init__(self, sender):
        super().__init__()
        self.send = sender
        self.signals.connect(sender.callback)
        myo.init()

    def timed_out(self):
        if (not self.connected) and self.connecting:
            self.send.add_log("Connection timed out!")
            self.disconnect()

    def connect(self):
        if not self.connected and not self.connecting:
            self.connecting = True
            self.stop = False
            QTimer.singleShot(5000, self.timed_out)  #Let's wait for 5 seconds
            self.send.add_log("Trying to connect to Myo (connection will timeout in 5 seconds)")
            self.start()

    def run(self):
        try:
            self.listener = Listener(self)
            hub = myo.Hub("com.twins.emgdataset")

            while hub.run(self.listener.on_event, 500):
                if self.stop:
                    self.stop = False
                    break
        except:
            self.connecting = False
            self.send.add_log("An error has occured!")

    def disconnect(self):
        if self.connected:
            self.send.add_log("Disconnected!")
            self.signals.emit({"type": EventType.disconnected, "data": {}})
        self.connecting = False
        self.connected = False
        self.stop = True
