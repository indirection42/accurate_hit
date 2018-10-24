import argparse
from datetime import datetime
from datetime import timedelta

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QTimer, QUrl, QDir, QPoint
from PyQt5.QtGui import QPainter, QPen, QPolygon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from PyQt5.QtWidgets import QApplication, QProgressBar, QPushButton, QTextEdit, QMessageBox, QLabel

parser = argparse.ArgumentParser(description='hit-game')
parser.add_argument('--tolerance', dest='tolerance', type=int, default=3, help='容许相差的天数')
parser.add_argument('--total_times', dest='total_times', type=int, default=5, help='暂停时光机的次数')
parser.add_argument('--ratio', dest='ratio', type=float, default=1, help='控制进度条的速度,数值越小速度越快')
args = parser.parse_args()

class Event():
    def __init__(self, event_name,  event_time):
        self.event_name = event_name
        self.event_time = datetime.strptime(str(event_time), "%Y%m%d")



class MainWindow(QtWidgets.QWidget):
    def __init__(self, event_list):
        QtWidgets.QWidget.__init__(self)
        self.left = 0
        self.top = 0
        self.width = 1440
        self.height = 900
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle('一锤定音')



        # variables initialization
        self.all_event_list=event_list
        self.passed_days = 0
        self.page = 0
        self.start_time = datetime.strptime('20110101', '%Y%m%d')


        self.step=0

        self.total_times = args.total_times
        self.tolerance = args.tolerance
        self.hit_times=0
        self.cnt=0



        # progress bar initialization
        self.pbar = QProgressBar(self)
        self.pbar_width = self.width * 0.95
        self.pbar_height = 20
        self.pbar_left = (self.width - self.pbar_width) / 2
        self.pbar_top = self.height * 0.4
        self.pbar_max = 370 * args.ratio
        self.pbar.setGeometry(self.pbar_left, self.pbar_top, self.pbar_width, self.pbar_height)
        self.pbar.setRange(0, self.pbar_max)


        # textedits and polylines initialization
        self.textedit_list=[]
        self.points_list = []
        self.textedit_height = self.height * 0.3
        self.textedit_num = 5
        self.base_html = "<html><body><h2>h2_placeholder</h2><p>p_placeholder</p></body></html>"
        for i in range(self.textedit_num):
            textedit = QTextEdit(self)
            textedit.setGeometry(self.left + self.width / self.textedit_num * i, self.top,
                self.width / self.textedit_num, self.textedit_height)
            self.textedit_list.append(textedit)
        # self.nextPage()


        # push button initialization
        self.start_button = QPushButton('Start', self)
        self.start_button.setFocusPolicy(Qt.NoFocus)
        self.button_width = 100
        self.button_height = 50
        self.start_button_left = self.width*0.4
        self.start_button_top = self.height * 0.5
        self.start_button.setGeometry(self.start_button_left, self.start_button_top, self.button_width,
            self.button_height)

        self.reset_button = QPushButton('Reset', self)
        self.reset_button.setFocusPolicy(Qt.NoFocus)
        self.reset_button_left = self.start_button_left
        self.reset_button_top = self.height * 0.7
        self.reset_button.setGeometry(self.reset_button_left, self.reset_button_top, self.button_width,
            self.button_height)

        # label initialization
        self.label1=QLabel(self)
        self.label_width = 400
        self.label_height=50
        self.label1_left=self.width*0.7
        self.label1_top=self.height*0.5
        self.label1.setGeometry(self.label1_left,self.label1_top,self.label_width,self.label_height)
        # self.label1.setText("你击中了{}次".format(self.cnt))

        self.label2=QLabel(self)
        self.label2_left=self.width*0.7
        self.label2_top=self.height*0.7
        self.label2.setGeometry(self.label2_left,self.label2_top,self.label_width,self.label_height)
        # self.label2.setText("你还有{}次机会".format(self.total_times-self.hit_times))

        self.label3 = QLabel(self)
        self.label3_left = self.width * 0.7
        self.label3_top = self.height * 0.6
        self.label3.setGeometry(self.label3_left, self.label3_top, self.label_width, self.label_height)
        # self.label3.setText("上次你距离最近的事件只差了{}天".format('x'))

        # timer initialization
        self.timer = QTimer()
        self.timeout_interval = 1




        # connect signals and slots
        self.start_button.clicked.connect(self.hit)
        self.reset_button.clicked.connect(self.reset)
        self.timer.timeout.connect(self.stepPlus)

        self.show()
        self.reset()
        # QMessageBox.information(self, "游戏规则", "本游戏你一共有{}次按钮机暂停时间的机会，当击中的日期和最近的事件日期相差{}天以内时，即算击中，总共有{}个事件，最后将根据击中事件数的多少发放奖励".format(self.total_times,self.tolerance,len(self.all_event_list)), QMessageBox.Ok)


    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key()==Qt.Key_Return:
            self.hit()
        elif QKeyEvent.key()==Qt.Key_Escape:
            self.close()

    def paintEvent(self, QPaintEvent):
        painter = QPainter()
        painter.begin(self)
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        painter.setPen(pen)
        for points in self.points_list:
            painter.drawPolyline(QPolygon(points))
        painter.end()


    def stepPlus(self):
        if self.step>self.pbar_max:
            if self.page < 5:
                self.step = 0
                self.passed_days += self.days_this_page
                self.nextPage()
            else:
                self.timer.stop()
                self.start_button.setText('Start')
                QMessageBox.information(self, "",
                    "时光机回到了现在，本次游戏中你一共成功了{}次，学院的发展离不开大家的支持，让我们一起努力吧，也许有一天你也能成为这些进展的主角！".format(self.cnt),
                    QMessageBox.Ok)
                self.reset()
        else:
            self.step = self.step + 1
        self.pbar.setValue(self.step)
        now = self.start_time + timedelta(int(self.step / self.pbar_max * self.days_this_page + self.passed_days))
        now_str = now.strftime("%Y{}%m{}%d{}").format('年', '月', '日')
        self.pbar.setFormat(now_str)


    def hit(self):
        if self.timer.isActive():
            if self.hit_times < self.total_times:
                self.hit_times += 1
                self.timer.stop()
                self.start_button.setText('Start')
                self.testHit(int(self.pbar.value() / self.pbar_max * self.days_this_page + self.passed_days))
                self.updateLabel()
            if self.hit_times == self.total_times:
                QMessageBox.information(self, "",
                    "时光机回到了现在，本次游戏中你一共成功了{}次，学院的发展离不开大家的支持，让我们一起努力吧，也许有一天你也能成为这些进展的主角！".format(self.cnt),
                    QMessageBox.Ok)
                self.reset()
        else:
            self.timer.start(self.timeout_interval)
            self.start_button.setText('Stop')



    def reset(self):
        self.timer.stop()
        self.start_button.setText('Start')
        self.pbar.reset()
        self.step = 0
        self.hit_times=0
        self.cnt=0
        self.page = 0
        self.passed_days = 0
        self.nextPage()
        self.updateLabel()
        self.update()
        QMessageBox.information(self, "时光穿梭机-游戏规则",
            "过去的十年里，我们学院取得了一些进展，现在让我们一起坐着时光机来回顾一下吧。。。本游戏你一共有{}次暂停时光机的机会，当时光机停下的日期和最近的事件日期相差{}天以内时，即算成功1次，总共有{}个事件，最后将根据成功次数发放奖励".format(
                self.total_times, self.tolerance, len(self.all_event_list)), QMessageBox.Ok)

    def testHit(self, value):
        diffs=[]
        # print((self.start_time+timedelta(value)).strftime('%Y%m%d'))
        for event in self.event_list:
            days = (event.event_time - self.start_time).days
            diffs.append(abs(value-days))
        # print(diffs)
        if min(diffs)<self.tolerance:
            self.label3.setText("上次你的时光机停在了正确的时间哦")
            self.cnt += 1
        else:
            self.label3.setText("上次你的时光机距离最近的事件只相差了{}天".format(min(diffs)))

    def nextPage(self):
        self.event_list = self.all_event_list[self.page * 5:(self.page + 1) * 5]
        self.days_this_page = int(((self.event_list[4].event_time - self.start_time).days - self.passed_days) * 1.01)
        self.points_list = []
        for i in range(len(self.event_list)):
            html = self.base_html.replace('h2_placeholder',
                datetime.strftime(self.event_list[i].event_time, "%Y{}%m{}%d{}").format('年', '月', '日'))
            html = html.replace('p_placeholder', self.event_list[i].event_name)
            self.textedit_list[i].setHtml(html)
            self.textedit_list[i].setReadOnly(True)
            days = (self.event_list[i].event_time - self.start_time).days - self.passed_days
            points = []
            points.append(
                QPoint(self.left + self.width / self.textedit_num * (i + 0.5), self.top + self.textedit_height))
            points.append(QPoint(self.left + self.width / self.textedit_num * (i + 0.5),
                self.pbar_top - (self.pbar_top - self.top - self.textedit_height) / (self.textedit_num + 1) * (i + 1)))
            points.append(QPoint(self.pbar_left + days / self.days_this_page * self.pbar_width,
                self.pbar_top - (self.pbar_top - self.top - self.textedit_height) / (self.textedit_num + 1) * (i + 1)))
            points.append(QPoint(self.pbar_left + days / self.days_this_page * self.pbar_width, self.pbar_top))
            self.points_list.append(points)
        self.update()
        self.page += 1

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
    with open('./major_events.txt',encoding='utf-8') as event_file:
        lines=event_file.readlines()
        for line in lines:
            line=line.strip()
            event=line.split('#')
            event_list.append(Event(event[0],event[1]))
    event_list.sort(key=lambda x: x.event_time)

    main_window = MainWindow(event_list)

    app.exec_()
