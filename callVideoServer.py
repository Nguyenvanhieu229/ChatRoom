import socket
import cv2
import pickle
import struct
import threading

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 9999))
server_socket.listen(10)

def send_video(client_socket, addr):
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        data = pickle.dumps(frame)
        message_size = struct.pack("L", len(data))
        client_socket.sendall(message_size + data)

def handle_client(client_socket, addr):
    video_thread = threading.Thread(target=send_video, args=(client_socket, addr))
    video_thread.start()

while True:
    client_socket, addr = server_socket.accept()
    print(f"Connection from {addr}")
    client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
    client_handler.start()
