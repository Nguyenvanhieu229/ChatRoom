# import socket library
import socket
# import threading library
import threading
import os
import random
import time
import pickle
from part_of_file import PartOfFile


# Choose a port that is free
PORT = 2209

# An IPv4 address is obtained
# for the server.
SERVER = "localhost"

# Address is stored as a tuple
ADDRESS = (SERVER, PORT)

# the format in which encoding
# and decoding will occur
FORMAT = "utf-8"

# Lists that will contains
# all the clients connected to
# the server and their names.
clients = {}
rooms = {}
part_of_files = {}

def creat_id(length):
    return random.choice([i for i in range(10 ** length, 10 ** (length+1) - 1)])

# Create a new socket for
# the server
server = socket.socket(socket.AF_INET,
                       socket.SOCK_STREAM)

# bind the address of the
# server to the socket
server.bind(ADDRESS)


# function to start the connection


def startChat():
    print("server is working on " + SERVER)

    # listening for connections
    server.listen(10)

    while True:
        # accept connections and returns
        # a new connection to the client
        #  and  the address bound to it
        conn, addr = server.accept()
        thread = threading.Thread(target=handle,
                                  args=(conn, addr))
        thread.start()


# method to handle the
# incoming messages


def create_new_client(conn):
    data = conn.recv(1024).decode('utf-8')
    id_client = str(creat_id(3))
    clients[id_client] = {'name': data}
    conn.sendall(f"Your id is : {id_client}".encode('utf-8'))

def create_new_room(conn, addr):

    #Nhan id nguoi dung
    id_client = conn.recv(1024).decode('utf-8')

    # Tao phong moi
    room_id = str(creat_id(5))
    rooms[room_id] = {'member' : [id_client], 'msgs' : [], 'connections': [conn], 'addr':[{'addr':addr, 'port':id_client}]}

    conn.sendall(f"Create your room : {room_id}".encode('utf-8'))

def join_room(conn, addr):

    #Nhan id nguoi dung
    id_client = conn.recv(1024).decode('utf-8')
    conn.sendall(f"received your id: {id_client}".encode("utf-8"))
    print(f"id client: {id_client}")


    #nhan id phong
    id_room = conn.recv(1024).decode('utf-8')

    if id_room not in rooms:
        conn.sendall(f"NoRoom".encode('utf-8'))
        return

    print(f"id room: {id_room}")
    conn.sendall(f"Join success : {id_room}".encode('utf-8'))

    rooms[id_room]['member'].append(id_client)
    rooms[id_room]['connections'].append(conn)
    rooms[id_room]['addr'].append({'addr':addr, 'port':id_client})

    quang_ba(id_client, id_room, "has joined the room!", 'text')



def new_text_message(conn):

    id_client = conn.recv(1024).decode('utf-8')
    conn.sendall(f"Your client id: {id_client}".encode('utf-8'))

    id_room = conn.recv(1024).decode('utf-8')
    conn.sendall(f"Your room id: {id_room}".encode("utf-8"))

    msg = conn.recv(1024).decode('utf-8')
    conn.sendall(f"Received your message: {msg}".encode('utf-8'))

    quang_ba( id_client, id_room, msg, "text")
    print("ok")



def handle(conn, addr):
    print(f"new connection {addr}")
    connected = True

    while connected:
        try:
            type_msg = conn.recv(1024).decode('utf-8')
            conn.sendall(f"Already for {type_msg} message".encode('utf-8'))
            if type_msg == 'name':
                create_new_client(conn)
            elif type_msg == 'create_room':
                create_new_room(conn, addr)
            elif type_msg == 'text_message':
                new_text_message(conn)
            elif type_msg == "join_room":
                join_room(conn, addr)
            elif type_msg == "part_of_file":
                received_part_of_file(conn)

        except Exception as e:
            print(e)
            connected = False

    conn.close()

# method for broadcasting
# messages to the each

def send_part_of_file(part_file, client):
    try:
        print(f"start send to {client}")
        conn = socket.socket(socket.AF_INET,
                               socket.SOCK_STREAM)
        addr = (client['addr'][0], int(client['port']))
        conn.connect(addr)
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
            conn.sendall(data_to_send[count: count+32768])
            rep = conn.recv(1024).decode("utf-8")
            count += 32768

        msg = conn.recv(1024).decode("utf-8")
        print(msg)
    except:
        pass

def received_part_of_file(conn):
    try:
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
        obj.client_name = clients[obj.client]['name']
        threads = []
        for client in rooms[obj.room]['addr']:
            thread = threading.Thread(target=lambda : send_part_of_file(obj, client))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        conn.sendall("Success".encode('utf-8'))
    except:
        pass

def send_text_message(id_room, msg_to_send, client):
    con = socket.socket(socket.AF_INET,
                         socket.SOCK_STREAM)
    addr = (client['addr'][0], int(client['port']))
    con.connect(addr)
    con.sendall("text".encode('utf-8'))
    con.recv(1024)
    con.sendall(id_room.encode('utf-8'))
    con.recv(1024)
    con.sendall(msg_to_send)
    con.recv(1024)
    print(f"gửi thành công cho {msg_to_send}")



def quang_ba(id_client, id_room, msg, type_data):
    print("bat dau gui quang ba")
    if id_client not in rooms[id_room]['member']:
        return
    client_name = clients[id_client]['name']
    msg_to_send = f"{client_name} : {msg}".encode('utf-8')

    for client in rooms[id_room]['addr']:
        print(type_data)
        if type_data == 'text':
            new_thread = threading.Thread(target=lambda : send_text_message(id_room, msg_to_send, client))
            new_thread.start()

# call the method to
# begin the communication
startChat()
server.close()