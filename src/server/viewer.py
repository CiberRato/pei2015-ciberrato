import socket

def main():
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	sock.sendto("<View/>\n" ,("127.0.0.1", 6000))

    send_socket.connect(("127.0.0.1", TCP_PORT))
	while 1:
		data, (host, port) = sock.recvfrom(1024)
		print data
        send_socket.send(data)

    send_socket.close()
    sock.close()

if __name__ == "__main__":
	main()
