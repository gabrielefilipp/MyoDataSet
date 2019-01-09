from PyQt5.QtWidgets import QListView, QAbstractItemView
from PyQt5.Qt import QKeyEvent, QStringListModel

class GestureListView(QListView):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setModel(QStringListModel())
        model:QStringListModel = self.model()

    def keyPressEvent(self, event:QKeyEvent):
        super().keyPressEvent(event)
        if self.currentIndex():
            if event.key() == 16777219:
                self.model().removeRow(int(self.currentIndex()))