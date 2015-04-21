import multiprocessing
import time
import re
from manager import *
from serverEndpoints import *

def main():

	manager = Manager()
	manager = multiprocessing.Process(target=manager.main)
	manager.daemon = True
	manager.start()
	print "Manager has been started.."

	time.sleep(0.5)
	endPoint = EndPoint()
	endPoint = multiprocessing.Process(target=endPoint.start)
	endPoint.daemon = False
	endPoint.start()
	print "Webservice has been started.."

	manager.join()

if __name__ == "__main__":
	main()
