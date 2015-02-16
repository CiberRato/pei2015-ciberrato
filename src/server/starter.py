#encoding=utf-8
import subprocess
import socket
import time
import os

def main():
	print "Process ID: ", os.getpid()
	print "Opening process for simulator"
	simulator = subprocess.Popen("./iia-myrob/cibertools/simulator-adapted/simulator", shell=True, stdout=subprocess.PIPE)
	# NOTE
	# Tem de ser garantido que o simulador esteja completamente em execução, tem de haver garantias
	time.sleep(1)
	print "Opening process for viewer"
	viewer = subprocess.Popen("python viewer.py", shell=True, stdout=subprocess.PIPE)
	# NOTE
	# Tem de ser garantido que o viewer esteja completamente em execução
	time.sleep(1)

	viewer_c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	viewer_c.connect(("127.0.0.1", 7000))


	
	print "Opening process for agent"
	# Falta verificar os problemas com o tipo de código que entra
	agent = subprocess.Popen("python iia-myrob/cibertools/myrob.py", shell=True, stdout=subprocess.PIPE)
	time.sleep(1)
	# Envia sinal ao viewer a dizer que está tudo em ordem para começar
	viewer_c.send("<StartedAgents/>")
	# Fica a espera de novidades do viewer
	print "Waiting for simulation to end"
	print viewer_c.recv(4096)
	print "Closing and killing"
	viewer_c.close()	

	agent.terminate()
	viewer.terminate()
	subprocess.Popen.kill(simulator)
	#simulator.wait()
	#print simulator.returncode

if __name__ == "__main__":
    main()