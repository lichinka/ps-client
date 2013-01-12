### Usage : python psservice.py install (or / then start, stop, remove)
### Author: dejan@petelin.si
### Windows service template by: Ryan Robitaille

import ctypes
import win32security
import win32service
import win32serviceutil
import win32api
import win32con
import win32event
import win32evtlogutil
import BaseHTTPServer
import os, sys, string, time, thread
import traceback
import servicemanager
import flask
import multiprocessing

class psservice(win32serviceutil.ServiceFramework):

	_svc_name_ = "PSclient"
	_svc_display_name_ = "Power Server client"
	_svc_description_ = "Smarter power management"

	def __init__(self, args):
		win32serviceutil.ServiceFramework.__init__(self, args)
		self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
		self.isAlive = True


	def SvcStop(self):
		self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
		win32event.SetEvent(self.hWaitStop)
		# write a message in the SM (optional)
        #import servicemanager
        #servicemanager.LogInfoMsg("aservice - Recieved stop signal")
		self.isAlive = False

	def SvcDoRun(self):
		servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,servicemanager.PYS_SERVICE_STARTED,(self._svc_name_, ''))

		app.run(host='0.0.0.0',port=2550)

        # Write a 'started' event to the event log... (not required)
        # win32evtlogutil.ReportEvent(self._svc_name_,servicemanager.PYS_SERVICE_STARTED,0, servicemanager.EVENTLOG_INFORMATION_TYPE,(self._svc_name_, ''))

        # methode 1: wait for beeing stopped ...
        # win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

		self.timeout = 1000	  # 1 seconds
		# This is how long the service will wait to run / refresh itself (see script below)

		while self.isAlive:
			# Wait for service stop signal, if I timeout, loop again
			rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
			# Check to see if self.hWaitStop happened
			if rc == win32event.WAIT_OBJECT_0:
				# Stop signal encountered
				servicemanager.LogInfoMsg("%s - STOPPED!"%self._svc_name_)  #For Event Log
				break

        # and write a 'stopped' event to the event log (not required)
        # win32evtlogutil.ReportEvent(self._svc_name_,servicemanager.PYS_SERVICE_STOPPED,0, servicemanager.EVENTLOG_INFORMATION_TYPE,(self._svc_name_, ''))

		self.ReportServiceStatus(win32service.SERVICE_STOPPED)
		return

app = flask.Flask(__name__)

@app.route('/')
def hello_world():
	return 'PowerServer!'

@app.route('/sleep/')
def sleep():
	try:
		thread.start_new_thread(power_state, (True, True))
		return 'OK'
	except Exception as e:
		return 'error: %s'%e

@app.route('/status/')
def status():
	return 'UP'

def power_state(suspend, force):
	# waits for one second in order the client to send the response first
	time.sleep(1)

	# Enable the SeShutdown privilege (which must be present in your token in the first place)
	priv_flags = win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY
	hToken = win32security.OpenProcessToken(win32api.GetCurrentProcess (), priv_flags)
	priv_id = win32security.LookupPrivilegeValue(None, win32security.SE_SHUTDOWN_NAME)
	old_privs = win32security.AdjustTokenPrivileges(hToken, 0, [(priv_id, win32security.SE_PRIVILEGE_ENABLED)])

	# Params:
	# True=> Standby; False=> Hibernate
	# True=> Force closedown; False=> Don't force
	ctypes.windll.kernel32.SetSystemPowerState(suspend, force)

def ctrlHandler(ctrlType):
	return True

#if __name__ == '__main__':
#	win32api.SetConsoleCtrlHandler(ctrlHandler, True)
#	win32serviceutil.HandleCommandLine(psservice)
