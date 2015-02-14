import subprocess
import time

def main():
	print "Opening process for simulator"
	simulator = subprocess.Popen("simulator_here", shell=True, stdout=subprocess.PIPE)
	# NOTE
	# Tem de ser garantido que o simulador esteja completamente em execução, tem de haver garantias
	time.sleep(5)
	print "Opening process for viewer"
	agent = subprocess.Popen("python viewer.py", shell=True, stdout=subprocess.PIPE)
	# NOTE
	# Tem de ser garantido que o viewer esteja completamente em execução
	time.sleep(5)
	print "Opening process for agent"
	# Falta verificar os problemas com o tipo de código que entra
	agent = subprocess.Popen("agent_program_execution_here", shell=True, stdout=subprocess.PIPE)

	#simulator.wait()
	#print simulator.returncode

if __name__ == "__main__":
    main()