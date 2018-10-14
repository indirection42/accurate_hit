from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QProgressBar, QPushButton, QTextEdit


class Event():
    def __init__(self, event_name: str, event_details: str, event_time: int):
        self.event_name = self.event_name
        self.event_details = self.event_details
        self.event_time = self.event_time  # used for locate on progress bar
        self.event_time_str = str(self.event_time)  # TODO appropriate formatting


class MainWindow(QtWidgets.QWidget):
    def __init__(self, event_list):
        QtWidgets.QWidget.__init__(self)
        self.left = 0
        self.top = 0
        self.width = 1000
        self.height = 500
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle('ProgressBar')

        # labels initialization
        self.textedit_list = []
        self.textedit_height = self.height * 0.3
        self.textedit_num = len(event_list)
        for i in range(len(event_list)):
            textedit = QTextEdit(self)
            textedit.setGeometry(self.left + self.width / self.textedit_num * i, self.top,
                self.width / self.textedit_num, self.textedit_height)
            textedit.textCursor().insertHtml('placeholder')
            textedit.setReadOnly(True)
            self.textedit_list.append(textedit)

        # progress bar initialization
        self.pbar = QProgressBar(self)
        self.pbar_width = self.width * 0.95
        self.pbar_height = 20
        self.pbar_left = (self.width - self.pbar_width) / 2
        self.pbar_top = self.height * 0.4
        self.pbar_max = 1000
        self.pbar.setGeometry(self.pbar_left, self.pbar_top, self.pbar_width, self.pbar_height)
        self.pbar.setRange(0, self.pbar_max)
        self.pbar.setFormat('%v')

        # push button initialization
        self.start_button = QPushButton('Start', self)
        self.start_button.setFocusPolicy(Qt.NoFocus)
        self.button_width = 100
        self.button_height = 50
        self.start_button_left = (self.width - self.button_width) / 2
        self.start_button_top = self.height * 0.5
        self.start_button.setGeometry(self.start_button_left, self.start_button_top, self.button_width,
            self.button_height)

        self.reset_button = QPushButton('Reset', self)
        self.reset_button.setFocusPolicy(Qt.NoFocus)
        self.reset_button_left = self.start_button_left
        self.reset_button_top = self.height * 0.7
        self.reset_button.setGeometry(self.reset_button_left, self.reset_button_top, self.button_width,
            self.button_height)

        # timer initialization
        self.timer = QTimer()
        self.timeout_interval = 100

        # variables initialization
        self.step = 0

        # connect signals and slots
        self.start_button.clicked.connect(self.start)
        self.reset_button.clicked.connect(self.reset)
        self.timer.timeout.connect(self.stepPlus)

    def stepPlus(self):
        self.step = self.step + 1
        self.pbar.setValue(self.step)

    def start(self):
        if self.timer.isActive():
            self.timer.stop()
            self.start_button.setText('Start')
        else:
            self.timer.start(self.timeout_interval)
            self.start_button.setText('Stop')

    def reset(self):
        self.timer.stop()
        self.start_button.setText('Start')
        self.step = 0
        self.pbar.setValue(self.step)



if __name__ == "__main__":
    app = QApplication([])
    app.setStyle('Fusion')
    event_list = [1, 2, 3]
    main_window = MainWindow(event_list)
    main_window.show()
    app.exec_()
