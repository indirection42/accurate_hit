import argparse
from datetime import datetime
from datetime import timedelta

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QTimer, QUrl, QDir, QPoint
from PyQt5.QtGui import QPainter, QPen, QPolygon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from PyQt5.QtWidgets import QApplication, QProgressBar, QPushButton, QTextEdit, QMessageBox, QLabel, QVBoxLayout, \
    QGroupBox, QHBoxLayout

parser = argparse.ArgumentParser(description='hit-game')
parser.add_argument('--tolerance', dest='tolerance', type=int, default=1, help='容许相差的天数')
parser.add_argument('--total_times', dest='total_times', type=int, default=25, help='暂停时光机的次数')
parser.add_argument('--timeout_interval', dest='timeout_interval', type=int, default=50, help='控制进度条速度，数值越小速度越快')
args = parser.parse_args()


class Event():
    def __init__(self, eventName, eventTime):
        self.eventName = eventName
        self.eventTime = datetime.strptime(str(eventTime), "%Y%m%d")


class PointsPaint(QtWidgets.QWidget):
    def __init__(self, parentWindow):
        self.parentWindow = parentWindow

    def updatePoints(self, pointsList):
        self.pointsList = pointsList
        self.update()

    def paintEvent(self, QPaintEvent):
        painter = QPainter()
        painter.begin(self)
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        painter.setPen(pen)
        for points in self.pointsList:
            painter.drawPolyline(QPolygon(points))
        painter.end()


class MainWindow(QtWidgets.QWidget):

    def __init__(self, eventList):
        super().__init__()
        self.left = 0
        self.top = 0
        self.width = 1440
        self.height = 900
        self.initUI()

        # variables initialization
        self.allEventList = eventList
        self.passedDays = 0
        self.page = 0
        self.startTime = datetime.strptime('20110301', '%Y%m%d')

        self.step = 0

        self.totalTimes = args.total_times
        self.tolerance = args.tolerance
        self.hitTimes = 0
        self.cnt = 0

        # timer initialization
        self.timer = QTimer()
        self.timeoutInterval = args.timeout_interval

        # connect signals and slots
        self.startButton.clicked.connect(self.hit)
        self.resetButton.clicked.connect(self.reset)
        self.timer.timeout.connect(self.stepPlus)

        self.show()

    def createTextEdits(self):
        self.textEdits = QGroupBox()
        layout = QHBoxLayout()
        self.textEditList = []
        for i in range(5):
            textEdit = QTextEdit(self)
            layout.addWidget(textEdit)
            self.textEditList.append(textEdit)
        self.textEdits.setLayout(layout)

    def createLeftLabels(self):
        self.leftLabels = QGroupBox()
        layout = QVBoxLayout()
        self.label = QLabel(self.leftLabels)
        layout.addWidget(self.label)
        self.leftLabels.setLayout(layout)

    def createRightLabels(self):
        self.rightLabels = QGroupBox()
        layout = QVBoxLayout()
        self.cntLabel = QLabel('up', self.rightLabels)
        self.leftChanceLabel = QLabel('center', self.rightLabels)
        self.errorTimeLabel = QLabel('down', self.rightLabels)
        layout.addWidget(self.cntLabel)
        layout.addWidget(self.leftChanceLabel)
        layout.addWidget(self.errorTimeLabel)
        self.rightLabels.setLayout(layout)

    def createCenterButtons(self):
        self.centerButtons = QGroupBox()
        layout = QVBoxLayout()
        self.startButton = QPushButton('Start', self.centerButtons)
        self.startButton.setFocusPolicy(Qt.NoFocus)
        self.resetButton = QPushButton('Reset', self.centerButtons)
        self.resetButton.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(self.startButton)
        layout.addWidget(self.resetButton)
        self.centerButtons.setLayout(layout)

    def createLabelsandButtons(self):
        self.labelsAndButtons = QGroupBox()
        self.createLeftLabels()
        self.createCenterButtons()
        self.createRightLabels()
        layout = QHBoxLayout()
        layout.addWidget(self.leftLabels)
        layout.addWidget(self.centerButtons)
        layout.addWidget(self.rightLabels)
        self.labelsAndButtons.setLayout(layout)

    def createProgressBar(self):
        self.progressBar = QProgressBar(self)
        self.progressBarMax = 250
        # self.progressBar.setGeometry(0,0,self.width*0.95,20)
        self.progressBar.setRange(0, self.progressBarMax)

    def createPointsPaint(self):
        self.PointsPaint = PointsPaint(self, parentWindow=self)

    def initUI(self):
        self.setWindowTitle('一锤定音')
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.mainLayout = QVBoxLayout()
        self.createTextEdits()
        self.createProgressBar()
        self.createLabelsandButtons()
        self.mainLayout.addWidget(self.textEdits)
        self.mainLayout.addWidget(self.PointsPaint)
        self.mainLayout.addWidget(self.progressBar)
        self.mainLayout.addWidget(self.labelsAndButtons)
        self.setLayout(self.mainLayout)

    def updateTextEdits(self):
        self.baseHtml = "<html><body><h2>h2_placeholder</h2><p>p_placeholder</p></body></html>"
        self.eventList = self.allEventList[self.page * 5:(self.page + 1) * 5]
        self.daysThisPage = int(((self.eventList[4].eventTime - self.startTime).days - self.passedDays) * 1.01)
        self.pointsList = []
        for i in range(len(self.eventList)):
            html = self.baseHtml.replace('h2_placeholder',
                datetime.strftime(self.eventList[i].eventTime, "%Y{}%m{}%d{}").format('年', '月', '日'))
            html = html.replace('p_placeholder', self.eventTist[i].eventName)
            self.texteditList[i].setHtml(html)
            self.texteditList[i].setReadOnly(True)
            days = (self.eventList[i].eventTime - self.startTime).days - self.passedDays
            points = []
            points.append(
                QPoint(self.left + self.width / self.textEditNum * (i + 0.5), self.top + self.textEditHeight))
            points.append(QPoint(self.left + self.width / self.textedit_num * (i + 0.5),
                self.pbar_top - (self.pbar_top - self.top - self.textedit_height) / (self.textedit_num + 1) * (i + 1)))
            points.append(QPoint(self.pbar_left + days / self.days_this_page * self.pbar_width,
                self.pbar_top - (self.pbar_top - self.top - self.textedit_height) / (self.textedit_num + 1) * (i + 1)))
            points.append(QPoint(self.pbar_left + days / self.days_this_page * self.pbar_width, self.pbar_top))
            self.points_list.append(points)
        self.update()
        self.page += 1

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Return:
            self.hit()
        elif QKeyEvent.key() == Qt.Key_Escape:
            self.close()

    def stepPlus(self):
        if self.step > self.progressBarMax:
            if self.page < 5:
                self.step = 0
                self.passed_days += self.days_this_page
                self.nextPage()
            else:
                self.timer.stop()
                self.startButton.setText('Start')
                QMessageBox.information(self, "",
                    "时光机回到了现在，本次游戏中你一共成功了{}次，学院的发展离不开大家的支持，让我们一起努力吧，也许有一天你也能成为这些进展的主角！".format(self.cnt),
                    QMessageBox.Ok)
                self.reset()
        else:
            self.step = self.step + 1
        self.progressBar.setValue(self.step)
        now = self.start_time + timedelta(int(self.step / self.progressBarMax * self.days_this_page + self.passed_days))
        now_str = now.strftime("%Y{}%m{}%d{}").format('年', '月', '日')
        self.progressBar.setFormat(now_str)

    def hit(self):
        if self.timer.isActive():
            if self.hit_times < self.total_times:
                self.hit_times += 1
                self.timer.stop()
                self.startButton.setText('Start')
                self.testHit(
                    int(self.progressBar.value() / self.progressBarMax * self.days_this_page + self.passed_days))
                self.updateLabel()
            if self.hit_times == self.total_times:
                QMessageBox.information(self, "",
                    "时光机回到了现在，本次游戏中你一共成功了{}次，学院的发展离不开大家的支持，让我们一起努力吧，也许有一天你也能成为这些进展的主角！".format(self.cnt),
                    QMessageBox.Ok)
                self.reset()
        else:
            self.timer.start(self.timeout_interval)
            self.startButton.setText('Stop')

    def reset(self):
        self.timer.stop()
        self.startButton.setText('Start')
        self.progressBar.reset()
        self.step = 0
        self.hit_times = 0
        self.cnt = 0
        self.page = 0
        self.passed_days = 0
        self.nextPage()
        self.updateLabel()
        self.update()
        QMessageBox.information(self, "时光穿梭机-游戏规则",
            "过去的十年里，我们学院取得了一些进展，现在让我们一起坐着时光机来回顾一下吧。。。本游戏你一共有{}次暂停时光机的机会，当时光机停下的日期和最近的事件日期相差{}天以内时，即算成功1次，总共有{}个事件，最后将根据成功次数发放奖励".format(
                self.total_times, self.tolerance, len(self.all_event_list)), QMessageBox.Ok)

    def testHit(self, value):
        diffs = []
        # print((self.start_time+timedelta(value)).strftime('%Y%m%d'))
        for event in self.event_list:
            days = (event.event_time - self.start_time).days
            diffs.append(abs(value - days))
        # print(diffs)
        if min(diffs) <= self.tolerance:
            self.label3.setText("上次你的时光机停在了正确的时间哦")
            self.cnt += 1
        else:
            self.label3.setText("上次你的时光机距离最近的事件只相差了{}天".format(min(diffs)))

    def updateLabel(self):
        self.label1.setText("你成功了{}次".format(self.cnt))
        self.label2.setText("你还有{}次暂停时光机的机会哦".format(self.total_times - self.hit_times))


if __name__ == "__main__":
    app = QApplication([])
    app.setStyle('Fusion')

    # music load and player initialization
    playlist = QMediaPlaylist()
    filenames = ['background.mp3']
    for filename in filenames:
        fullpath = QDir.current().absoluteFilePath(filename)
        url = QUrl.fromLocalFile(fullpath)
        playlist.addMedia(QMediaContent(url))
    playlist.setPlaybackMode(QMediaPlaylist.Loop)
    player = QMediaPlayer()
    player.setPlaylist(playlist)
    # player.play()

    # events load and initilization
    event_list = []
    with open('./major_events.txt', encoding='utf-8') as event_file:
        lines = event_file.readlines()
        for line in lines:
            line = line.strip()
            event = line.split('#')
            event_list.append(Event(event[0], event[1]))
    event_list.sort(key=lambda x: x.event_time)

    main_window = MainWindow(event_list)

    app.exec_()
