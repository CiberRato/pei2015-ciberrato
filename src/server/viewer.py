import socket

def main():
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
	sock.sendto("<View/>\n" ,("127.0.0.1", 6000))

	while 1:
		data, (host, port) = sock.recvfrom(1024)
		print data

if __name__ == "__main__":
	main()
