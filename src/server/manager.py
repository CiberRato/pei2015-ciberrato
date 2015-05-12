import socket
from threading import Thread
from multiprocessing import Queue
from multiprocessing import Process
from multiprocessing import Array
from starter import *
from testReceiver import *
from serverEndpoints import *

class Manager:
	def main(self):
		# Loading settings
		settings_str = re.sub("///.*", "", open("settings.json", "r").read())
		settings = json.loads(settings_str)

		GET_SIM_HOST = settings["settings"]["starter_end_point_host"]
		GET_SIM_PORT = settings["settings"]["starter_end_point_port"]

		# Create thread to launch end point
		endPoint = EndPoint()
		endPoint = Thread(target=endPoint.start)

		print "[MANAGER] Manager is in deamon mode"
		end_point_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		end_point_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		end_point_tcp.bind((GET_SIM_HOST, GET_SIM_PORT))
		end_point_tcp.listen(1)

		endPoint.start()
		end_point_c, end_point_add = end_point_tcp.accept()


		# Creating Shared QUEUEs
		simulations = Queue()
		tests = Queue()

		# Launching Thread to handle simulations
		sims = Sims(simulations)
		handle_sims_thread = Thread(target=sims.handle_sims)
		handle_sims_thread.start()

		# Launching Thread to handle tests
		test = Tests(tests)
		handle_tests_thread = Thread(target=test.handle_tests)
		handle_tests_thread.start()

		# Waiting for a post to be done
		data = None
		while 1:
			print "[MANAGER] Waiting for post.."
			while data == None or data == "":
				data = end_point_c.recv(1024)

			arg = data.split("&")
			if len(arg) == 1:
				trial_id = arg[0].split("=")
				# Add simulation to queue
				simulations.put(trial_id[1])

			elif len(arg) == 2:
				team_name = arg[0].split("=")
				agent_name = arg[1].split("=")
				# Add test to queue
				tests.put((team_name[1],agent_name[1]))


			data = None


		end_point_c.shutdown(socket.SHUT_RDWR)
		end_point_c.close()
		end_point_tcp.shutdown(socket.SHUT_RDWR)
		end_point_tcp.close()

		handle_sims_thread.join()
		handle_tests_thread.join()

class Sims:
	def __init__(self, sims):
		print "[HANDLE SIMS] Thread started"
		self.simulations = sims

	def handle_sims(self):
		# Loading settings
		settings_str = re.sub("///.*", "", open("settings.json", "r").read())
		settings = json.loads(settings_str)

		MAX_SIMULATIONS = settings["settings"]["max_simulations"]

		# Creating Shared Semaphore
		semaphore = threading.Semaphore(value=MAX_SIMULATIONS)

		# Creating shared array to store ports being used
		ports = Array("i", MAX_SIMULATIONS)

		while 1:
			sim_id = self.simulations.get(block=True)
			semaphore.acquire()
			port = 0
			for i in range(6000, 6000+MAX_SIMULATIONS):
				if not i in ports:
					port = i
					break
				else:
					continue
			if port == 0:
				print "[MANAGER] Error in assigning ports"
				continue
			print "[MANAGER] Received simulation with sim_id=" + sim_id + ", starting now on port " + str(port)
			starter = Starter()
			starter_thread = Thread(target=starter.main, args=(sim_id, port, ports, semaphore))
			starter_thread.start()

class Tests:
	def __init__(self, t):
		print "[HANDLE TESTS] Thread started"
		self.tests = t

	def handle_tests(self):
		while 1:
			team_name, agent_name = self.tests.get(block=True)
			print "[TESTS] Received test request with agent_name: " + agent_name + " team_name:" + team_name + ", starting now.."
			test = Test()
			test_thread = Thread(target=test.run, args=(team_name, agent_name,))
			test_thread.start()
			test_thread.join()


if __name__ == "__main__":
	manager = Manager()
	manager_thread = Process(target=manager.main)
	manager_thread.deamon = True
	manager_thread.start()
	manager_thread.join()
