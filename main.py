import socket
import random
import sys
from threading import Thread

from PyInstaller.compat import system
from PyQt5 import QtGui, QtWidgets,QtCore
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, \
    QMainWindow, QTextEdit, QSplitter, QPushButton, QMessageBox

from server import procces, IP as ip, PORT as port

r = random.randrange(0, 255)
g = random.randrange(0, 255)
b = random.randrange(0, 255)

separator_token = "<SEP>"

s = socket.socket()
start = False



class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ip_address_input = QTextEdit()
        self.ip_address_input.setPlaceholderText('IP-адрес...')
        self.ip_address_input.installEventFilter(self)
        self.port_input = QTextEdit()
        self.port_input.setPlaceholderText('Порт...')
        self.port_input.installEventFilter(self)
        self.connect_button = QPushButton('Connect...')
        self.start_server_button = QPushButton('Запустить сервер и подключиться...')
        self.nickname_edit = QTextEdit()
        self.nickname_edit.installEventFilter(self)
        self.nickname_edit.setPlaceholderText('Введите логин...')
        self.nickname_button = QPushButton('✔')
        self.nickname_button.setMaximumSize(50, 40)
        self.setWindowIcon(QtGui.QIcon('assets/logo.ico'))
        self.setWindowTitle('Chat 0.1.2a')
        self.plain_text_edit = QTextEdit()
        self.plain_text_edit.setReadOnly(True)
        self.plain_text_edit.setMinimumWidth(800)
        self.text_edit_log = QTextEdit()
        self.text_edit_log.installEventFilter(self)
        self.text_edit_log.setWordWrapMode(QtGui.QTextOption.WrapMode.NoWrap)
        self.text_edit_log.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_log.setMaximumHeight(50)
        self.text_edit_log.setPlaceholderText('Введите сообщение...')
        self.plain_text_edit.setStyleSheet(f'color: rgb({r},{g},{b})')
        self.send_button = QPushButton('Отправить')

        h1_splitter = QSplitter(Qt.Horizontal)
        h1_splitter.addWidget(self.nickname_edit)
        h1_splitter.addWidget(self.nickname_button)
        h1_splitter.addWidget(self.ip_address_input)
        h1_splitter.addWidget(self.port_input)
        h1_splitter.addWidget(self.connect_button)

        h_splitter = QSplitter(Qt.Horizontal)
        h_splitter.addWidget(self.plain_text_edit)

        v_splitter = QSplitter(Qt.Vertical)
        v_splitter.addWidget(h1_splitter)
        v_splitter.addWidget(h_splitter)
        v_splitter.addWidget(self.text_edit_log)
        v_splitter.addWidget(self.send_button)
        v_splitter.addWidget(self.start_server_button)


        self.setCentralWidget(v_splitter)
        self.send_button.clicked.connect(self.on_click_button)

        self.nickname_button.clicked.connect(self.on_click_user_button)

        self.connect_button.clicked.connect(self.connect_to_server)
        self.start_server_button.clicked.connect(self.start_server)

    def eventFilter(self, obj, event):
        if obj is self.text_edit_log and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.on_click_button()
                return True
        elif obj is self.nickname_edit and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.on_click_user_button()
                return True
        elif obj is self.ip_address_input and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                return True
        elif obj is self.port_input and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.connect_to_server()
                return True
        return super().eventFilter(obj, event)

    def on_click_button(self):
        if self.nickname_edit.toPlainText() == '':
            self.plain_text_edit.append('Введите логин!')


        else:
            nickname = self.nickname_edit.toPlainText()
            mesg = self.text_edit_log.toPlainText()
            to_send = f'{nickname}: {mesg}'.encode('utf8')
            try:
                s.send(to_send)
            except:
                self.plain_text_edit.append(f'Сообщение не отправлено: {mesg}')
            self.text_edit_log.clear()

    def on_click_user_button(self):
        self.nickname_edit.setReadOnly(True)
        self.nickname_button.setDisabled(True)

    def listen_for_messages(self):
        while True:
            msg = s.recv(1024).decode()
            if self.nickname_edit.toPlainText() in msg:
                self.plain_text_edit.setAlignment(Qt.AlignRight)
                self.plain_text_edit.append(f'{msg}')
            else:
                self.plain_text_edit.setAlignment(Qt.AlignLeft)
                self.plain_text_edit.append(f'{msg}')


    def connect_to_server(self):
        if self.nickname_edit.toPlainText() == '' or self.nickname_edit.isReadOnly() == False:
            self.plain_text_edit.append('Введите логин')
        else:
            self.plain_text_edit.append(f'[*] Подключение к  серверу...')
            try:
                if self.ip_address_input.toPlainText() == '':
                    print(2)
                    s.connect((ip, port))
                else:
                    print(self.ip_address_input.toPlainText())
                    print(int(self.port_input.toPlainText()))
                    s.connect((self.ip_address_input.toPlainText(), int(self.port_input.toPlainText())))
            except OSError as e:
                if e.winerror == 10056:
                    self.plain_text_edit.append(f'[*]Вы уже подключены.')
                else:
                    self.plain_text_edit.append(f'[*]Сервер недоступен.')
            else:
                self.plain_text_edit.append('[*] подключено.')
                # s.send(f'[*]{self.nickname_edit.toPlainText()} присоединился[*]'.encode('utf8'))
                self.ip_address_input.setReadOnly(True)
                self.port_input.setReadOnly(True)
                self.connect_button.setDisabled(True)
                th3 = Thread(target=self.listen_for_messages)
                # th3.daemon = True
                th3.start()

    def start_server(self):
        if self.nickname_edit.toPlainText() == '' or self.nickname_edit.isReadOnly() == False:
            self.plain_text_edit.append('Введите логин!')

        else:
            self.plain_text_edit.append(f'[*]Сервер запущен на: {ip}:{port}')
            th1 = Thread(target=procces)
            th1.start()
            th2 = Thread(target=self.connect_to_server)
            th2.start()

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            'Информация',
            "Вы уверены, что хотите закрыть приложение?",
            QMessageBox.Yes, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            system.exit()

            super(MainWindow, self).closeEvent(event)
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fushion')
    app.setFont(QFont('Comic Sans MS', 15))
    mw = MainWindow()
    mw.setMaximumWidth(800)
    mw.show()
    sys.exit(app.exec_())
