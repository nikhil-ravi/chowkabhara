import socket
from _thread import start_new_thread
import sys

server = "localhost"
port = 8080

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print("Error creating socket: %s" % e)

s.listen(2)
print("Waiting for connection, server started")


def threaded_client(conn):
    conn.send(str.encode("Connected."))
    reply = ""
    while True:
        try:
            data = conn.recv(2048)
            reply = data.decode("utf-8")
            if not data:
                print("Disconnected")
                break
            else:
                print(f"Received: {reply}")
                print(f"Sending: {reply}")

            conn.sendall(str.encode(reply))
        except Exception as e:
            raise e
    print("Lost connection.")
    conn.close()


while True:
    conn, addr = s.accept()
    print(f"Connected to: {addr}")
    threaded_client(conn)

    start_new_thread(threaded_client, (conn,))
