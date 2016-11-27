def broadcast_to_chat(room_ref,join_id,conn,chat_rooms,data):
	for join_id, conn in chat_rooms[room_ref].iteritems():
		conn.send(data)

class ChatRoom:

	def __init__(self,host,port):
		self.host = host
		self.port = port

	def join_chatroom(self,chat_rooms,room,client_name,room_ref,join_id,conn):
		if room_ref not in chat_rooms:
			chat_rooms[room_ref] = {}
		if join_id not in chat_rooms[room_ref]:
			chat_rooms[room_ref][join_id] = conn
			conn.send("JOINED_CHATROOM:%s\nSERVER_IP:%s\nPORT:%s\nROOM_REF:%s\nJOIN_ID:%s\n"
				%(str(room),self.host,self.port,str(room_ref),str(join_id)))
			message = ("CHAT:%s\nCLIENT_NAME:%s\nMESSAGE:%s has joined this chatroom.\n\n" 
				%(str(room_ref),str(client_name),str(client_name)))
			broadcast_to_chat(room_ref,join_id,conn,chat_rooms,message)

	def leave_chatroom(self,chat_rooms,room_ref,join_id,client_name,conn):
		conn.send("LEFT_CHATROOM:%s\nJOIN_ID:%s\n" %(str(room_ref),str(join_id)))
		message = ("CHAT:%s\nCLIENT_NAME:%s\nMESSAGE:%s has left this chatroom.\n\n"
			%(str(room_ref),str(client_name),str(client_name),))
		broadcast_to_chat(room_ref,join_id,conn,chat_rooms,message)
		del chat_rooms[room_ref][join_id]

	def disconnect(self,chat_rooms,client_name,join_id,conn,activeConnection):
		for room_ref in chat_rooms.keys():
			if join_id in chat_rooms[room_ref]:
				message = ("CHAT:%s:\nCLIENT_NAME:%s\nMESSAGE:%s has left this chatroom.\n\n"
					%(str(room_ref),str(client_name),str(client_name)))
				broadcast_to_chat(room_ref,join_id,conn,chat_rooms,message)
				if join_id in chat_rooms[room_ref]:
					del chat_rooms[room_ref][join_id]
		activeConnection = False

	def send_message(self,chat_rooms,room_ref,join_id,client_name,msg,conn):
		user_msg = ("CHAT:%s\nCLIENT_NAME:%s\nMESSAGE:%s\n\n" %(str(room_ref),str(client_name),msg))
		broadcast_to_chat(room_ref,join_id,conn,chat_rooms,user_msg)