# progressbar.py

from PyQt5.QtWidgets import QApplication, QProgressBar, QPushButton, QMessageBox, QLineEdit, QLabel
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QBasicTimer
from PyQt5.QtGui import QPainter, QPen, QPainterPath
from random import randint
def process_time(time_event):
    locate_num_event = []
    for group in time_event:
        event = []
        for sub_group in group:
            sub_event = []
            for (num1, num2, text, flag) in group:
                locate_num = ((num1 - 1) * 30 + num2) / 365 * 100
                sub_event.append([locate_num, text, flag])
            event.append(sub_event)
    return event



time_event = [
                [
                    [10, 28, "ZJU ranks third in the China!", False],
                    [2, 1, "ZJU ranks second in the China!", False],
                    [6, 5, "ZJU ranks first in the China!", False]
                ],
                [
                    [2, 3, "ZJU ranks tenth in the World!", False],
                    [7, 9, "ZJU ranks fifth in the world!", False],
                    [12, 9, "ZJU ranks first in the world!", False]
                ]
            ]

# turn time to percent
locate_num_event = process_time(time_event)

class ProgressBar(QtWidgets.QWidget):
    def __init__(self, time_event, parent= None):
        QtWidgets.QWidget.__init__(self)
        app.setStyle('Fusion')
        len_time_event = len(time_event)
        print("len = ", len_time_event)
        self.num = randint(0, len_time_event - 1)
        self.select_time_event = time_event[self.num]

        self.bias = 3
        self.sub_group_num = 3

        self.window_title = "ProgressBar"

        self.window_left = 1200
        self.window_top = 1200
        self.window_width = 1000
        self.window_height = 600

        self.bar_left = 200
        self.bar_top = 400
        self.bar_width = 600
        self.bar_height = 100

        self.initUI(self.select_time_event)
    
    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawLines(qp)
        qp.end()
    
    
    def initUI(self, sub_time_event):
        # sub_time_event is a sub list of time_event
        assert len(sub_time_event) >= 1
        
        #self.setGeometry(300, 300, 250, 150)
        self.setGeometry(self.window_left, self.window_top, self.window_width, self.window_height)
        self.setWindowTitle(self.window_title)
        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(self.bar_left, self.bar_top, self.bar_width, self.bar_height)

        
        self.button = QPushButton('Start', self)
        self.button.setFocusPolicy(Qt.NoFocus)
        self.button.move(480, 540)
        
        self.button.clicked.connect(self.onStart)
        self.timer = QBasicTimer()
        self.step = 0

        start_wide = 50
        start_height = 50

        for locate_num, text, flag in self.select_time_event:
            label = QLabel(text, self)
            label.move(start_wide, start_height)
            #path = QPainterPath()
            #path.moveTo(self.window_left + locate_num, self.window_top)
            #qp.drawLine(start_wide, start_height, self.window_left + locate_num, self.window_top)
            start_height += 100
            start_wide += 300
        self.show()
    
    def drawLines(self, qp):

        # set letter
        start_wide = 50
        start_height = 50
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        #qp.setPen(pen)
        

        for locate_num, text, flag in self.select_time_event:
            #label = QLabel(text, self)
            #label.move(start_wide, start_height)
            #path = QPainterPath()
            #path.moveTo(self.window_left + locate_num, self.window_top)
            qp.setPen(pen)
            print("num = ", locate_num)
            qp.drawLine(start_wide + 40, start_height + 15, self.bar_left + (locate_num / 100) * self.bar_width, self.bar_top)
            start_height += 100
            start_wide += 300



        
    def timerEvent(self, event):
        if self.step >=100:
            self.timer.stop()
            return
        self.step = self.step + 1
        self.pbar.setValue(self.step)
        for i in range(self.sub_group_num):
            locate_num, text, flag = self.select_time_event[i]
            if not flag:
                if (locate_num > (self.step - self.bias)) and (locate_num < (self.step + self.bias)):
                    QMessageBox.about(self, "You win!",text)
                    #self.text.setFocus()
                    self.select_time_event[i][2] = True
                    self.timer.stop()
                    self.button.setText('Start')

        
    def onStart(self):
        if self.timer.isActive(): 
            self.timer.stop()
            self.button.setText('Start')
        else:
            self.timer.start(100, self)
            self.button.setText('Stop')
        

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    qb = ProgressBar(locate_num_event)
    qb.show()
    sys.exit(app.exec_())