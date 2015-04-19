import threading
import socket

class Manager:
	def main(self):
		# Loading settings
		settings_str = re.sub("///.*", "", open("settings.json", "r").read())
		settings = json.loads(settings_str)

		END_POINT_HOST = settings["settings"]["starter_end_point_host"]
		END_POINT_PORT = settings["settings"]["starter_end_point_port"]

		print "[MANAGER] Manger is in deamon mode"
		end_point_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		end_point_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		end_point_tcp.bind((END_POINT_HOST, END_POINT_PORT))
		end_point_tcp.listen(1)
		end_point_c, end_point_add = end_point_tcp.accept()

		# Waiting for a post to be done
		data = None
		while 1:
			print "[MANAGER] Waiting for post.."
			while data == None or data == "":
				data = end_point_c.recv(1024)

			if arg == "sim_id":
				#handle simulation
				print "[MANAGER] Received simulation with sim_id= " + data + ", starting now.."

			else if arg == "agent_name":
				#handle test
			else:
				#ignore

			data = None

		end_point_c.shutdown(socket.SHUT_RDWR)
		end_point_c.close()
		end_point_tcp.shutdown(socket.SHUT_RDWR)
		end_point_tcp.close()
