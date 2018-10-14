from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QProgressBar, QPushButton, QLabel


class Event():
    def __init__(self, event_name: str, event_details: str, event_time: int):
        self.event_name = self.event_name
        self.event_details = self.event_details
        self.event_time = self.event_time  # used for locate on progress bar
        self.event_time_str = str(self.event_time)  # TODO appropriate formatting


class ProgressBar(QtWidgets.QWidget):
    def __init__(self, event_list):
        QtWidgets.QWidget.__init__(self)
        self.top = 300
        self.left = 300
        self.width = 250
        self.height = 150
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.setWindowTitle('ProgressBar')

        # self.label_num=len(event_list)
        # for i in range(len(event_list)):
        #     label=QLabel(self)
        #     label.setGeometry(self.top,self.left+self.width/self.label_num*i,self.width/self.label_num,self.height/self.label_num)
        #     label.setText('de')
        self.label = QLabel(self)

        self.pbar = QProgressBar(self)
        self.pbar_max = 1000
        self.pbar.setGeometry(30, 40, 200, 20)
        self.pbar.setRange(0, self.pbar_max)
        self.pbar.setFormat('%v')

        self.button = QPushButton('Start', self)
        self.button.setFocusPolicy(Qt.NoFocus)
        self.button.move(30, 80)

        self.button.clicked.connect(self.onStart)
        self.timer = QTimer()
        self.timer.timeout.connect(self.stepPlus)
        self.timeout_interval = 100
        self.step = 0

    def stepPlus(self):
        self.step = self.step + 1
        self.pbar.setValue(self.step)

    def onStart(self):
        if self.timer.isActive():
            self.timer.stop()
            self.button.setText('Start')
        else:
            self.timer.start(self.timeout_interval)
            self.button.setText('Stop')


if __name__ == "__main__":
    app = QApplication([])
    app.setStyle('Fusion')
    event_list = [1, 2, 3]
    qb = ProgressBar(event_list)
    qb.show()
    app.exec_()
