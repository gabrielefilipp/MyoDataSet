from PyQt5.QtWidgets import QListView, QAbstractItemView, QMenu, QAction
from PyQt5.Qt import QKeyEvent
from PyQt5.QtCore import QModelIndex, pyqtSignal

#data_w = ["train", "validation", "test"]
#data_g = ["left", "right", "fist", "ok", "point", "scissors", "pistol", "three", "five", "rabbit"]

class PListView(QListView):

    contextMenuShowed = pyqtSignal()
    contextMenuDifferenced = pyqtSignal()
    contextMenuAveraged = pyqtSignal()
    contextMenuShowedFinder = pyqtSignal()
    contextMenuMoved = pyqtSignal(QAction)
    contextMenuDeleted = pyqtSignal()

    def __init__(self, parent = None, style = "", project = None):
        super().__init__(parent)
        self.setStyleSheet(style)  # TODO: Fix out ouf mask cells (first and last)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.project = project

    def keyPressEvent(self, event:QKeyEvent):
        super().keyPressEvent(event)
        if self.currentIndex():
            if event.key() == 16777220:
                if self.hasFocus():
                    self.contextMenuShowed.emit()
            elif event.key() == 16777219:
                self.contextMenuDeleted.emit()

    def contextMenuEvent(self, event):
        indexes = self.selectedIndexes()

        if not len(indexes) == 0:
            menu = QMenu(self)
            menu.setStyleSheet("QMenu::item{background-color: white;color: black;}QMenu::item:selected{background-color: rgb(0, 99, 225);color: white;}")
            showAction = menu.addAction("View Data")

            differenceAction:QAction = menu.addAction("Difference")
            differenceAction.setVisible(len(indexes) == 2)

            averageAction = menu.addAction("Average")
            averageAction.setVisible(len(indexes) >= 2)

            showFinderAction = menu.addAction("Show in Finder")

            moveMenu = menu.addMenu("Move")

            for w in self.project["sets"]:
                m = moveMenu.addMenu(w)
                for g in self.project["gestures"]:
                    m.addAction(g)

            deleteAction = menu.addAction("Delete")

            action = menu.exec_(self.mapToGlobal(event.pos()))
            if action:
                if action == showAction:
                    self.contextMenuShowed.emit()
                elif action == differenceAction:
                    self.contextMenuDifferenced.emit()
                elif action == averageAction:
                    self.contextMenuAveraged.emit()
                elif action == showFinderAction:
                    self.contextMenuShowedFinder.emit()
                elif action == deleteAction:
                    self.contextMenuDeleted.emit()
                else:
                    self.contextMenuMoved.emit(action)
