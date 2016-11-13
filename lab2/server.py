import socket
import threading
import os
import sys


max = 10
address = "localhost"
port = int(sys.argv[1])
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
numberofThreads = 0
active = True
threadpool = []

def sortThreadPool():
        i = 0
        print "TEST"
        for thread in threadpool:
                if(not thread.isAlive()):
                        threadpool.pop(i)
                        global numberofThreads
                        numberofThreads = numberofThreads - 1
                i = i + 1
        threadpool.sort()

def handleClient(conn,addr):
    openCon = True
    while openCon:
        data = conn.recv(1024)
        if "HELO" in data:
            print "MSG recieved. Number of threads %d" % (numberofThreads)
            conn.send("%sIP:%s\nPort:%d\nStudentID:13328025\nSUCCESS" %(data,address,port))
        elif data == "KILL_SERVICE\n":
            print "Killing Service"
            sock.close()
            print "Socket closed"
            os._exit(1)
        elif not data:
            openCon = False
        else:
            print data

sock.bind((address,port))
print "Socket created at IP:%s and port:%d, now listening for clients" %(address,port)
sock.listen(5)
while active:
    if numberofThreads < max:
        conn,addr = sock.accept()
        threadpool.append(threading.Thread(target = handleClient, args =(conn,addr,)))
        threadpool[numberofThreads].start()
        global numberofThreads
        numberofThreads = numberofThreads + 1
    else:
        print "There are no free threads"