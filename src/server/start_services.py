import multiprocessing
import time
import re
from starter import *
from serverEndpoints import *

def main():

	starter = Starter()
	starter = multiprocessing.Process(target=starter.main)
	starter.daemon = True
	starter.start()
	print "Starter has been started.."

	time.sleep(0.5)
	endPoint = EndPoint()
	endPoint = multiprocessing.Process(target=endPoint.start)
	endPoint.daemon = True
	endPoint.start()
	print "Webservice has been started.."

	starter.join()

if __name__ == "__main__":
	main()
