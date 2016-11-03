import socket
import sys

def main():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	print >>sys.stderr, 'starting up' 
	sock.connect(("localhost", 8000))

	
	
	try:
		sock.sendall("GET /echo.php?message=hello_my_name_is_slim_shady HTTP/1.0\r\n\r\n")
		data = sock.recv(4096)

		while True:
			print >>sys.stderr, 'received "%s"' % data
   			data = sock.recv(4096)
   			if data == "":
   				break


   	finally:
   		print >>sys.stderr, 'closing socket'
   		sock.close()


if __name__ == '__main__':
	main()







