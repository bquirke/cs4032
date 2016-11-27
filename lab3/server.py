import collections
import os
import socket
import threading
from hashlib import md5
from chatroom import ChatRoom

port = 8220
host = '134.226.32.10'
student_id = "13328025"
chat_room = ChatRoom(host,port)
chat_rooms = collections.OrderedDict()

maxThreadCount = 1000
totalThreads = 0
runninG = True
threadPool = []
BUFF = 2048

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
the_address = (host,port)
sock.bind(the_address)
sock.listen(5)

def handleClientConnections(conn, address):
  while runninG:
    data = conn.recv(BUFF)

    if "HELO BASE_TEST" in data:
      conn.send("%sIP:%s\nPort:%d\nStudentID:%s" %(data,host,port,student_id))

    elif "KILL_SERVICE" in data:
      os._exit(1)

    elif "JOIN_CHATROOM" in data:
      data = data.split("\n")
      room = data[0].split(":")[1]
      client_name = data[3].split(":")[1]
      room_ref = int(md5(room).hexdigest(), 16)
      join_id = int(md5(client_name).hexdigest(), 16)
      chat_room.join_chatroom(chat_rooms,room,client_name,room_ref,join_id,conn)

    elif "LEAVE_CHATROOM" in data:
      data  = data.split("\n")
      room_ref = int(data[0].split(":")[1])
      join_id = int(data[1].split(":")[1])
      client_name = data[2].split(":")[1]
      chat_room.leave_chatroom(chat_rooms,room_ref,join_id,client_name,conn)
    
    elif "DISCONNECT" in data:
      data  = data.split("\n")
      client_name = data[2].split(":")[1]
      join_id = int(md5(client_name).hexdigest(), 16)
      chat_room.disconnect(chat_rooms,client_name,join_id,conn,runninG)
    
    elif "CHAT" in data:
      data  = data.split("\n")
      room_ref = int(data[0].split(":")[1])
      join_id = int(data[1].split(":")[1])
      client_name = data[2].split(":")[1]
      msg = data[3].split(":")[1]
      chat_room.send_message(chat_rooms,room_ref,join_id,client_name,msg,conn)

while runninG:
  if totalThreads < maxThreadCount:
    conn,address = sock.accept()
    threadPool.append(threading.Thread(target = handleClientConnections, args =(conn,address)))
    threadPool[totalThreads].start()
    global totalThreads
    totalThreads = totalThreads + 1
  else:
  	print "No available threads at this moment"
    