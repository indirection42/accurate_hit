from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QTimer,QUrl,QDir,QPoint,pyqtSignal
from PyQt5.QtWidgets import QApplication, QProgressBar, QPushButton, QTextEdit,QMessageBox,QLabel,QGroupBox,QVBoxLayout
from PyQt5.QtMultimedia import QMediaPlayer,QMediaPlaylist,QMediaContent
from PyQt5.QtGui import QPainter,QPen,QPolygon
from datetime import datetime
from datetime import timedelta
import random



class Event():
    def __init__(self, event_name,  event_time):
        self.event_name = event_name
        self.event_time = int(event_time)



class MainWindow(QtWidgets.QWidget):
    hitSignal=pyqtSignal(bool,int)
    def __init__(self, event_list):
        QtWidgets.QWidget.__init__(self)
        self.left = 0
        self.top = 0
        self.width = 1440
        self.height = 900
        self.setGeometry(self.left, self.top, self.width, self.height)
        # self.setWindowTitle('ProgressBar')


        # variables initialization
        self.all_event_list=event_list
        self.event_list=random.sample(self.all_event_list,5)
        self.event_list.sort(key=lambda x:x.event_time)
        self.start_time = datetime.strptime('20080101', '%Y%m%d')
        self.total_days=3700
        self.total_times=4
        self.step=0
        self.tolerance=10
        self.hit_times=0
        self.cnt=0




        # progress bar initialization
        self.pbar = QProgressBar(self)
        self.pbar_width = self.width * 0.95
        self.pbar_height = 20
        self.pbar_left = (self.width - self.pbar_width) / 2
        self.pbar_top = self.height * 0.4
        self.pbar_max = 370
        self.pbar.setGeometry(self.pbar_left, self.pbar_top, self.pbar_width, self.pbar_height)
        self.pbar.setRange(0, self.pbar_max)


        # textedits and polylines initialization
        self.textedit_list=[]
        self.points_list = []
        self.textedit_height = self.height * 0.3
        self.textedit_num = len(self.event_list)
        self.base_html = "<html><body><h2>h2_placeholder</h2><p>p_placeholder</p></body></html>"
        for i in range(self.textedit_num):
            textedit = QTextEdit(self)
            textedit.setGeometry(self.left + self.width / self.textedit_num * i, self.top,
                self.width / self.textedit_num, self.textedit_height)
            html = self.base_html.replace('h2_placeholder', str(self.event_list[i].event_time))
            html = html.replace('p_placeholder', self.event_list[i].event_name)
            textedit.setHtml(html)
            textedit.setReadOnly(True)
            days = (datetime.strptime(str(self.event_list[i].event_time), '%Y%m%d') - self.start_time).days
            points = []
            points.append(
                QPoint(self.left + self.width / self.textedit_num * (i + 0.5), self.top + self.textedit_height))
            points.append(QPoint(self.left + self.width / self.textedit_num * (i + 0.5),
                self.pbar_top - (self.pbar_top - self.top - self.textedit_height) / (self.textedit_num + 1) * (i + 1)))
            points.append(QPoint(self.pbar_left + days / self.total_days * self.pbar_width,
                self.pbar_top - (self.pbar_top - self.top - self.textedit_height) / (self.textedit_num + 1) * (i + 1)))
            points.append(QPoint(self.pbar_left + days / self.total_days * self.pbar_width, self.pbar_top))
            self.points_list.append(points)
            self.textedit_list.append(textedit)


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
        self.label_width=100
        self.label_height=50
        self.label1_left=self.width*0.7
        self.label1_top=self.height*0.5
        self.label1.setGeometry(self.label1_left,self.label1_top,self.label_width,self.label_height)
        self.label1.setText("击中次数"+str(self.cnt))

        self.label2=QLabel(self)
        self.label2_left=self.width*0.7
        self.label2_top=self.height*0.7
        self.label2.setGeometry(self.label2_left,self.label2_top,self.label_width,self.label_height)
        self.label2.setText("剩余尝试次数"+str(self.total_times-self.hit_times))


        # timer initialization
        self.timer = QTimer()
        self.timeout_interval = 1



        # connect signals and slots
        self.start_button.clicked.connect(self.hit)
        self.reset_button.clicked.connect(self.reset)
        self.timer.timeout.connect(self.stepPlus)
        self.hitSignal.connect(self.msg)


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
            self.step=0
        else:
            self.step = self.step + 1
        self.pbar.setValue(self.step)
        now=self.start_time+timedelta(self.step/self.pbar_max*self.total_days)
        now_str=now.strftime("%Y%m%d")
        self.pbar.setFormat(now_str)


    def hit(self):
        if self.timer.isActive() and self.hit_times<self.total_times:
            self.timer.stop()
            self.start_button.setText('Start')
            self.test_hit(self.pbar.value()/self.pbar_max*self.total_days)
            self.updateInfo()
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
        self.event_list=random.sample(self.all_event_list,3)
        self.event_list.sort(key=lambda x:x.event_time)
        self.sample()
        self.updateInfo()
        self.update()

    def test_hit(self,value):
        self.hit_times += 1
        diffs=[]
        print((self.start_time+timedelta(value)).strftime('%Y%m%d'))
        for event in self.event_list:
            days=(datetime.strptime(str(event.event_time),'%Y%m%d')-self.start_time).days
            diffs.append(abs(value-days))
        print(diffs)
        if min(diffs)<self.tolerance:
            self.hitSignal.emit(True,min(diffs))
        else:
            self.hitSignal.emit(False,min(diffs))

    def msg(self,status,value):
        if status is True:
            reply =QMessageBox.information(self,"result","You hit it! 和实际日期相差了{}天".format(value),QMessageBox.Ok)
        else:
            reply=QMessageBox.information(self,"result","Sorry, you did'nt hit it! 和实际日期相差了{}天".format(value),QMessageBox.Ok)

    def sample(self):
        self.event_list=random.sample(self.all_event_list,5)
        self.event_list.sort(key=lambda x:x.event_time)
        self.points_list = []
        for i in range(len(self.event_list)):
            html = self.base_html.replace('h2_placeholder', str(self.event_list[i].event_time))
            html = html.replace('p_placeholder', self.event_list[i].event_name)
            self.textedit_list[i].setHtml(html)
            days = (datetime.strptime(str(self.event_list[i].event_time), '%Y%m%d') - self.start_time).days
            points = []
            points.append(
                QPoint(self.left + self.width / self.textedit_num * (i + 0.5), self.top + self.textedit_height))
            points.append(QPoint(self.left + self.width / self.textedit_num * (i + 0.5),
                self.pbar_top - (self.pbar_top - self.top - self.textedit_height) / (self.textedit_num + 1) * (i + 1)))
            points.append(QPoint(self.pbar_left + days / self.total_days * self.pbar_width,
                self.pbar_top - (self.pbar_top - self.top - self.textedit_height) / (self.textedit_num + 1) * (i + 1)))
            points.append(QPoint(self.pbar_left + days / self.total_days * self.pbar_width, self.pbar_top))
            self.points_list.append(points)
    def updateInfo(self):
        self.label1.setText("击中次数"+str(self.cnt))
        self.label2.setText("剩余尝试次数"+str(self.total_times-self.hit_times))

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
    player.play()



    # events load and initilization
    event_list = []
    with open('./major_events.txt',encoding='utf-8') as event_file:
        lines=event_file.readlines()
        for line in lines:
            line=line.strip()
            event=line.split('#')
            event_list.append(Event(event[0],event[1]))


    main_window = MainWindow(event_list)

    main_window.show()
    app.exec_()
