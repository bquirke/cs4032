import socket
import sys
import os

msgType = int(sys.argv[1])

if msgType == 1:
	msg = "HELO text\n"

elif msgType == 2:
	msg = "KILL_SERVICE\n"

else:
	print >>sys.stderr, 'Invalid arguements, 1 for HELO & 2 for KILL_SERVICE'
	os._exit(1)

def main():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	print >>sys.stderr, 'starting up' 
	sock.connect(("localhost", 8000))
	connected = True

	
	
	try:
		sock.sendall(msg)
		data = sock.recv(4096)

		while True:
			print >>sys.stderr, 'received "%s"' % data
   			data = sock.recv(4096)
   			if data == "":
   				break
   			


   	finally:
   		print >>sys.stderr, 'closing socket\n'
   		sock.close()


if __name__ == '__main__':
	main()