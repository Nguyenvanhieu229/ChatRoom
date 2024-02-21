import math
import sys
import time
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QFileDialog
from PyQt5 import QtCore
from PyQt5.QtCore import QThread, Qt, pyqtSignal, Q_ARG, QObject, QMutex, QWaitCondition, QMutexLocker
import login
import chatroom
import room
import socket
from video import VideoPlayer
from queue import Queue
import threading
from part_of_file import PartOfFile
import pickle

import sys
import time
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QFileDialog
from PyQt5 import QtCore
from PyQt5.QtCore import QThread, Qt, pyqtSignal, Q_ARG, QObject, QMutex, QWaitCondition, QMutexLocker
import login
import chatroom
import room
import socket
from video import VideoPlayer
from queue import Queue
import threading

lock = False

PORT = 2209
SERVER = "localhost"
ADDRESS = (SERVER, PORT)
FORMAT = "utf-8"

# Create a new client socket
# and connect to the server

client = socket.socket(socket.AF_INET,
                       socket.SOCK_STREAM)
client.connect(ADDRESS)

rooms = {}
parts_file = {}
lock = False


def send_part_of_file(part_file):
    conn = socket.socket(socket.AF_INET,
                         socket.SOCK_STREAM)
    conn.connect(ADDRESS)
    conn.sendall("part_of_file".encode("utf-8"))
    rep = conn.recv(1024).decode("utf-8")
    print(rep)
    data_to_send = pickle.dumps(part_file)
    print(type(data_to_send))
    obj_size = len(data_to_send)
    conn.sendall(str(obj_size).encode("utf-8"))
    rep = conn.recv(1024).decode("utf-8")
    print(rep)
    print("start send")
    count = 0
    while count < obj_size:
        time.sleep(0.1)
        conn.sendall(data_to_send[count: count + 32768])
        rep = conn.recv(1024).decode("utf-8")
        count += 32768

    msg = conn.recv(1024).decode("utf-8")
    print(msg)
    parts_file[part_file.file_name]['num'] += 1

    global lock
    if not lock:
        lock = True
        window.ui_room.progress_bar.setValue(int(parts_file[part_file.file_name]['num'] / part_file.total_part * 100))
        if parts_file[part_file.file_name]['num'] == part_file.total_part:
            print("send_full")
            window.ui_room.progress_bar.setValue(100)
            time.sleep(0.2)
            window.ui_room.progress_bar.setValue(0)

        lock = False


def send_larger_file(file_name, client, room):
    parts_file[file_name] = {'num': 0}
    with open(file_name, 'rb') as fin:
        data = fin.read()
        size = len(data)
        count = 0
        i = 0
        size_part = int(size / (1048576 * 20))
        size_part = 1 if size_part == 0 else size_part

        while count < size:
            time.sleep(0.1)
            obj = PartOfFile(total_part=math.ceil(size / (size_part * 1048576)), file_name=file_name,
                             data=data[count:count + size_part * 1048576], order=i, client=client, room=room)
            thread = threading.Thread(target=lambda: send_part_of_file(obj))
            count += size_part * 1048576
            i += 1
            thread.start()


def start_connect(msg):
    client.sendall(msg.encode('utf-8'))
    rep = client.recv(1024).decode('utf-8')
    return rep[-4:]


def create_new_room(id_client, widget, conn):
    # gui id client
    conn.sendall(id_client.encode('utf-8'))
    rep = conn.recv(1024).decode('utf-8')
    print(rep)

    return rep[-6:]


def send_text(client_id, widget, conn):
    # gửi id
    conn.sendall(client_id.encode('utf-8'))
    rep = conn.recv(1024).decode('utf-8')
    print(rep)

    # gửi id phòng
    conn.sendall(widget.label_2.text().encode('utf-8'))
    rep = conn.recv(1024).decode('utf-8')
    print(rep)

    # gửi tin nhắn
    conn.sendall(widget.text_message.toPlainText().encode('utf-8'))
    rep = conn.recv(1024).decode('utf-8')
    print(rep)
    return rep


def join_room(id_client, widget, conn):
    # gửi id
    conn.sendall(id_client.encode('utf-8'))
    rep = conn.recv(1024).decode('utf-8')
    print(rep)

    # gửi id phòng
    conn.sendall(widget.lineEdit.text().encode('utf-8'))
    rep = conn.recv(1024).decode('utf-8')
    print(rep)

    return rep[-6:]


def send_message(type_message, widget, id_client, conn, id_room="", file_name=""):
    # gui thong thong bao kieu du lieu se gui tiep theo
    conn.sendall(type_message.encode('utf-8'))
    rep = conn.recv(1024).decode('utf-8')
    print(rep)

    # gui bang cac ham tuong ung voi du lieu
    if type_message == 'name':
        return start_connect(widget.txt_name.text())
    elif type_message == 'create_room':
        return create_new_room(id_client, widget, conn)
    elif type_message == 'text_message':
        return send_text(id_client, widget, conn)
    elif type_message == 'join_room':
        return join_room(id_client, widget, conn)


class ListenRoom(QThread):
    data_changed = pyqtSignal(dict)

    def __init__(self, port):
        super().__init__()
        self.server = socket.socket(socket.AF_INET,
                                    socket.SOCK_STREAM)
        self.addr = ('localhost', port)
        self.port = port
        self.server.bind(self.addr)
        self.part_of_files = {}

    def run(self):
        print("start room")
        self.server.listen(10)
        while True:
            conn, addr = self.server.accept()

            # Tao mot thread de nghe ngong moi khi co ket noi moi den
            thread = threading.Thread(target=lambda: self.handle(conn, addr))
            thread.start()

    def handle(self, conn, addr):
        print(f"New connection: {addr}")
        connected = True
        while connected:
            try:
                type_msg = conn.recv(1024).decode('utf-8')
                conn.sendall(f"Already for {type_msg} message".encode('utf-8'))
                if type_msg == 'part_of_file':
                    self.received_part_of_file(conn)
                elif type_msg == 'text':
                    self.received_text_message(conn)

            except Exception as e:
                print(e)
                connected = False

        conn.close()

    def received_part_of_file(self, conn):
        print("start")
        part_size = conn.recv(1024).decode("utf-8")
        part_size = int(part_size)
        conn.sendall(str(part_size).encode('utf-8'))
        count = 0
        data = b''
        while count < int(part_size):
            tmp = conn.recv(32768)
            conn.sendall("ok".encode('utf-8'))
            data += tmp
            count += 32768

        obj = pickle.loads(data)
        conn.sendall("Success".encode('utf-8'))
        if obj.file_name not in self.part_of_files:
            self.part_of_files[obj.file_name] = {'num_part': 1, 'part': [obj]}
            print(f"Add new file {obj.file_name}")
        else:
            self.part_of_files[obj.file_name]['num_part'] += 1
            self.part_of_files[obj.file_name]['part'].append(obj)
            print(f"Add new part:{obj.order}")

        if (self.part_of_files[obj.file_name]['num_part']) == obj.total_part:
            print("Get ALL part of file")
            time.sleep(1)
            self.part_of_files[obj.file_name]['part'].sort(key=lambda x: x.order)
            data = b''
            for part in self.part_of_files[obj.file_name]['part']:
                data += part.data
            file_name = str(self.port) + "_" + os.path.basename(obj.file_name)
            with open(file_name, 'wb') as fout:
                fout.write(data)
            self.data_changed.emit(
                {'to': obj.room, 'type_data': 'multi_file', 'nguon': obj.client_name, 'file_name': file_name, 'msg': 0})

    def received_text_message(self, conn):
        to = conn.recv(1024).decode('utf-8')
        conn.sendall("OK".encode('utf-8'))
        print(f"to {to}")
        msg = conn.recv(1024).decode('utf-8')
        conn.sendall("ok".encode('utf-8'))
        print(f"msg {msg}")
        self.data_changed.emit({'to': to, 'type_data': 'text', 'msg': msg})


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(480, 640)
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.login_widget = QWidget()
        self.stacked_widget.addWidget(self.login_widget)

        self.ui_login = login.Ui_Form()
        self.ui_login.setupUi(self.login_widget)
        self.ui_login.btn_start.clicked.connect(lambda: self.start_connection(self.ui_login))

        self.chatroom_widget = QWidget()
        self.stacked_widget.addWidget(self.chatroom_widget)

        self.ui_chatroom = chatroom.Ui_Form()
        self.ui_chatroom.setupUi(self.chatroom_widget)
        self.ui_chatroom.btn_create.clicked.connect(lambda: self.create_new_room(self.ui_chatroom))
        self.ui_chatroom.btn_join.clicked.connect(lambda: self.join_room(self.ui_chatroom))
        self.room_widget = QWidget()
        self.stacked_widget.addWidget(self.room_widget)

        self.ui_room = room.Ui_Form()
        self.ui_room.setupUi(self.room_widget)
        self.ui_room.btn_sendText.clicked.connect(lambda: self.send_new_text_message(self.ui_room))
        self.ui_room.btn_send_muti.clicked.connect(self.send_multi_mesage)

        self.name = None
        self.id_client = None
        self.id_room = None
        self.conns = []
        self.threads = []
        self.listeners = []
        self.stacked_widget.setCurrentIndex(0)

    def start_connection(self, widget):

        print("Clicked start")
        self.name = widget.txt_name.text()
        self.id_client = send_message('name', widget, self.id_client, client)

        # đổi giao diện sang chọn phòng
        self.stacked_widget.setCurrentIndex(1)

    def create_new_room(self, widget):

        conn = socket.socket(socket.AF_INET,
                             socket.SOCK_STREAM)
        conn.connect(ADDRESS)
        self.conns.append(conn)

        print("create a new room")
        id_room = send_message("create_room", widget, self.id_client, conn)
        self.id_room = id_room
        # Thay đổi id room trong cửa sổ
        _translate = QtCore.QCoreApplication.translate
        self.ui_room.label_2.setText(_translate("Form", id_room))

        # Chuyển cửa sổ phòng chat
        self.stacked_widget.setCurrentIndex(2)

        # rcv = threading.Thread(target=self.listen_to_server, args=(conn, self.ui_room))
        # rcv.start()

        rethr1 = QThread()
        print(self.id_client)
        listener1 = ListenRoom(int(self.id_client))
        listener1.moveToThread(rethr1)
        rethr1.started.connect(listener1.run)
        listener1.data_changed.connect(self.update_message)
        rethr1.start()
        print("ok")

        rooms[id_room] = {'connection': conn, 'messages': [], 'thread1': rethr1, 'listner1': listener1}

    def join_room(self, widget):

        conn = socket.socket(socket.AF_INET,
                             socket.SOCK_STREAM)
        conn.connect(ADDRESS)
        self.conns.append(conn)
        id_room = send_message("join_room", widget, self.id_client, conn)
        self.id_room = id_room

        if id_room == 'NoRoom':
            print("Not room")
            return

        # Thay đổi id room trong cửa sổ
        _translate = QtCore.QCoreApplication.translate
        self.ui_room.label_2.setText(_translate("Form", id_room))
        # Chuyển cửa sổ phòng chat
        self.stacked_widget.setCurrentIndex(2)

        rethr1 = QThread()
        print(self.id_client)
        listener1 = ListenRoom(int(self.id_client))
        listener1.moveToThread(rethr1)
        rethr1.started.connect(listener1.run)
        listener1.data_changed.connect(self.update_message)
        rethr1.start()
        print("ok")

        rooms[id_room] = {'connection': conn, 'messages': [], 'thread1': rethr1,
                          'listner1': listener1}

    def send_multi_mesage(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open Image File', r"<Default dir>",
                                                   "Multifile files (*.jpg *.jpeg *.gif *.png *.mp3 *.mp4)")
        if not file_name or file_name == "":
            return

        send_larger_file(file_name, self.id_client, self.id_room)


    def send_new_text_message(self, widget):

        send_message("text_message", widget, self.id_client, client)

        self.ui_room.text_message.setText("")

    def update_message(self, message):
        # Thay đổi thông tin trên giao diện
        room = message['to']
        data_type = message['type_data']
        msg = message['msg']
        rooms[room]['messages'].append(msg)
        if data_type == 'text':
            self.ui_room.add_text_message(msg)
        elif data_type == "multi_file":
            fr = message['nguon']
            file_name = message['file_name']

            if file_name[-4:] in ['.png', '.jpg']:
                self.ui_room.add_image_message(fr, file_name)
            elif file_name[-4:] in ['.mp4']:
                self.ui_room.add_video_message(fr, file_name)
            elif file_name[-4:] in ['.mp3', '.wav']:
                self.ui_room.add_audio_message(fr, file_name)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())



