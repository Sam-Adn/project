#! /usr/bin/python2.7
import sys

if sys.version_info[0] > 2:
    print("Must use Python 2")
    sys.exit()

import socket
import os
import struct

if len(sys.argv) != 3:
    print("wrong usage, use like this:\npython2 fileName ipAddress portNumber")
    sys.exit()
else:
    TCP_IP = sys.argv[1]
    TCP_PORT = int(sys.argv[2])

BUFFER_SIZE = 1024 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def put(file_name):
    print("\nUploading file: {}...".format(file_name))
    try:
        content = open(file_name, "rb")
    except:
        print("Couldn't open file. Make sure the file name was entered correctly.")
        return
    try:
        s.send("put")
    except Exception as e:
        print("Couldn't make server request. Make sure a connection has been established.")
        print(e)
        return
    try:
        s.recv(BUFFER_SIZE)
        s.send(struct.pack("h", sys.getsizeof(file_name)))
        s.send(file_name)
        s.recv(BUFFER_SIZE)
        s.send(struct.pack("i", os.path.getsize(file_name)))
    except:
        print("Error sending file details")
    try:
        l = content.read(BUFFER_SIZE)
        print("\nSending...")
        while l:
            s.send(l)
            l = content.read(BUFFER_SIZE)
        content.close()
        upload_time = struct.unpack("f", s.recv(4))[0]
        upload_size = struct.unpack("i", s.recv(4))[0]
        print("\nSent file: {}\nTime elapsed: {}s\nFile size: {}b".format(file_name, upload_time, upload_size))
    except:
        print("Error sending file")
        return
    return

def ls_files():
    print("Requesting files...\n")
    try:
        s.send("ls")
    except:
        print("Couldn't make server request. Make sure a connection has been established.")
        return
    try:
        text = s.recv(4096)
        print(text)
    except:
        print("Couldn't retrieve list")
        return


def get(file_name):
    print("Downloading file: {}".format(file_name))
    try:
        s.send("get")
    except:
        print("Couldn't make server request. Make sure a connection has been established.")
        return
    try:
        s.recv(BUFFER_SIZE)
        s.send(struct.pack("h", sys.getsizeof(file_name)))
        s.send(file_name)
        file_size = struct.unpack("i", s.recv(4))[0]
        if file_size == -1:
            print("File does not exist. Make sure the name was entered correctly")
            return
    except:
        print("Error checking file")
    try:
        s.send("1")
        output_file = open(file_name, "wb")
        bytes_recieved = 0
        print("\nDownloading...")
        while bytes_recieved < file_size:
            l = s.recv(BUFFER_SIZE)
            output_file.write(l)
            bytes_recieved += BUFFER_SIZE
        output_file.close()
        print("Successfully downloaded {}".format(file_name))
        s.send("1")
        time_elapsed = struct.unpack("f", s.recv(4))[0]
        print("Time elapsed: {}s\nFile size: {}b".format(time_elapsed, file_size))
    except:
        print("Error downloading file")
        return
    return

def quit():
    s.send("QUIT")
    s.recv(BUFFER_SIZE)
    s.close()
    print("Server connection ended")
    return

print("requesting server to connect...")
try:
    s.connect((TCP_IP, TCP_PORT))
    print("Connection sucessful")
except:
    print("Connection unsucessful. Make sure the server is online.")
    sys.exit()

print ("\n\nWelcome to the FTP client.\n\nCall one of the following functions:\nput  file_path : Upload file\nls             : List files\nget  file_path : Download file\nQUIT           : Exit")

while True:
    prompt = raw_input("\nftp> ")
    if prompt[:4].upper() == "CONN":
        conn()
    elif prompt[:3].upper() == "PUT":
        put(prompt[4:])
    elif prompt[:2].upper() == "LS":
        ls_files()
    elif prompt[:3].upper() == "GET":
        get(prompt[4:])
    elif prompt[:4].upper() == "QUIT":
        quit()
        break
    else:
        print("Command not recognised; please try again")
