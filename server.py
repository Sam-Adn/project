#! /usr/bin/python2.7
import sys

if sys.version_info[0] > 2:
    print("Must use Python 2")
    sys.exit()

import socket
import time
import os
import struct
from thread import *

TCP_IP = "127.0.0.1" 
if len(sys.argv) != 2:
    print("wrong usage, use like this: python2 fileName portNumber")
    sys.exit()
else:
    TCP_PORT = int(sys.argv[1])

print("\nFTP server-side.\n\nwaiting for a client to connect.")

BUFFER_SIZE = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(10)

def client(conn, addr):
    print("\nConnected to by address: {}".format(addr))
    def put():
        conn.send("1")
        file_name_size = struct.unpack("h", conn.recv(2))[0]
        file_name = conn.recv(file_name_size)
        conn.send("1")
        file_size = struct.unpack("i", conn.recv(4))[0]
        start_time = time.time()
        output_file = open(file_name, "wb")
        bytes_recieved = 0
        print("\nRecieving...")
        while bytes_recieved < file_size:
            l = conn.recv(BUFFER_SIZE)
            output_file.write(l)
            bytes_recieved += BUFFER_SIZE
        output_file.close()
        print("\nRecieved file: {}".format(file_name))
        conn.send(struct.pack("f", time.time() - start_time))
        conn.send(struct.pack("i", file_size))
        return

    def ls_files():
        print("Listing files...")
        text = ""
        i = 1
        for File in os.listdir(os.getcwd()):
            text += "\t"+str(i)+"- " + File + "\n" 
            i += 1
        text += "total count: " + str(i)
        conn.send(text)
        print("Successfully sent list")
        return

    def get():
        conn.send("1")
        file_name_length = struct.unpack("h", conn.recv(2))[0]
        print(file_name_length)
        file_name = conn.recv(file_name_length)
        print(file_name)
        if os.path.isfile(file_name):
            conn.send(struct.pack("i", os.path.getsize(file_name)))
        else:
            print("File name not valid")
            conn.send(struct.pack("i", -1))
            return
        conn.recv(BUFFER_SIZE)
        start_time = time.time()
        print("Sending file...")
        content = open(file_name, "rb")
        l = content.read(BUFFER_SIZE)
        while l:
            conn.send(l)
            l = content.read(BUFFER_SIZE)
        content.close()
        conn.recv(BUFFER_SIZE)
        conn.send(struct.pack("f", time.time() - start_time))
        return

    def quit():
        conn.send("1")
        conn.close()
        print("a connection has been ended")

    while True:
        try:
            data = conn.recv(BUFFER_SIZE)
        except:
            pass
        if data == "put":
            put()
        elif data == "ls":
            ls_files()
        elif data == "get":
            get()
        elif data == "QUIT":
            quit()
        data = None

while True:
    conn, addr = s.accept()
    print(addr[0] + " connected")
    try:
        start_new_thread(client,(conn, addr))
    except:
        pass
server.close()
