import multiprocessing
import time
import re
from starter import *
from get_sim_id import *

def main():

	starter = Starter()
	starter = multiprocessing.Process(target=starter.main)
	starter.daemon = True
	starter.start()
	print "Starter has been started.."

	# time.sleep(3)
	# endPoint = GetSimId()
	# endPoint = multiprocessing.Process(target=endPoint.__init__)
	# endPoint.daemon = True
	# endPoint.start()
	# print "Get Sim Id End-Point has been started.."


	starter.join()


if __name__ == "__main__":
	main()