#from datastructure import formatQueue, transQueue
from datastructure import LogManager, FormatManager#, GetConfigure
#import json
import datetime
import os, sys
#import threading
#import time

def background():
	try:
		pid = os.fork()
	
		if pid > 0:
			print("PID: %d" % pid)
			sys.exit()

	except OSError as error:
		print("Unable to fork. Error: %d (%s)" %(error.errno, error.strerror))
		sys.exit()
	
	doTask()

def doTask():
	os.setsid()

	os.open("/dev/null", os.O_RDWR)
	os.dup(0)
	os.dup(0)

	lm = LogManager(datetime.datetime.now())
	fm = FormatManager()

	lm.start()
	fm.start()

if __name__ == '__main__':
	background()
