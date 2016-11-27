import math
import struct
import socket
import select
import threading

_HOST = '192.168.1.102'
_PORT = 8220

class ChatServer(threading.Thread):

	MAX_WAITING_CONNECTIONS = 10
	RECV_BUFFER = 4096
	RECV_MSG_LEN = 4

	def __init__(self, host, port):
		threading.Thread.__init__(self)
		self.host = host
		self.port = port
		self.connections = []
		self.running = True

		self.room_names = {}
		self.room_ref = 1

		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server_socket.bind((self.host, self.port))
		self.server_socket.listen(self.MAX_WAITING_CONNECTIONS)
		self.connections.append(self.server_socket)

		

	def _broadcast(self, client_socket, client_message):

		for sock in self.connections:
			is_not_the_server = sock != self.server_socket
			is_not_the_client_sending = sock != client_socket # May not need this as the msg may have to be sent back
			if is_not_the_server and is_not_the_client_sending:
				try:
					sock.send(client_message)

				except socket.error:
					sock.close()
					self.connections.remove(sock)


	def _run(self):

		while self.running:

			try:
				ready_to_read, ready_to_write, in_error = select.select(self.connections, [], [], 60)
			except socket.error:
				continue

			else:
				for sock in ready_to_read:
					if sock == self.server_socket:
						try:
							# Handles a new client connection
							client_socket, client_address = self.server_socket.accept()
						except socket.error:
							break

						else:
							self.connections.append(client_socket)
							print "Client (%s, %s) JOINED_CHATROOM" % client_address
							self._broadcast(client_socket, "\n[%s:%s] entered the chat room... JOINED_CHATROOM\n" % client_address)


					else:
						
						data = sock.recv(self.RECV_BUFFER)
						if data:
							print "Recieved data"
							self._broadcast(sock, "\r" + '<' + str(sock.getpeername()) + '> ' + data)


		self.stop()



	def stop(self):
		self.running = False
		self.server_socket.close()


if __name__ == '__main__':
	chat_server = ChatServer(_HOST, _PORT)
	chat_server._run()
