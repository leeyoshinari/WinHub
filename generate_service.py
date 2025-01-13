#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import os
import time
import subprocess
from win32serviceutil import ServiceFramework, HandleCommandLine
import win32service
import win32event
import servicemanager


def get_variable(key):
    return os.environ.get(key, '')


class MyService(ServiceFramework):
    _svc_name_ = "WinHubService"
    _svc_display_name_ = "WinHubService"
    _svc_description_ = "A service to run WinHub"

    def __init__(self, args):
        ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.process = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        if self.process:
            self.process.terminate()
            self.process.wait()
        
        self.restart_service()

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED, (self._svc_name_, ''))
        while True:
            rc = win32event.WaitForSingleObject(self.hWaitStop, 30000)
            if rc == win32event.WAIT_OBJECT_0:
                servicemanager.LogInfoMsg("WinHubService - STOPPED!")
                break
            else:
                try:
                    if not self.process or self.process.poll() is not None:
                        project_path = os.path.dirname(os.path.abspath(__file__))
                        command = ["uvicorn", "main:app", "--host", f"{get_variable('winHubHost')}", "--port", f"{get_variable('winHubPort')}"]
                        self.process = subprocess.Popen(command, cwd=project_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        servicemanager.LogInfoMsg("WinHubService - Started!")
                except Exception as e:
                    servicemanager.LogErrorMsg(f"WinHubService - Error starting process: {e}")
                    break
                if self.process.poll() is not None:
                    servicemanager.LogInfoMsg("WinHubService - Process Exited, restarting")
                    time.sleep(3)
                    self.SvcStop()
                    time.sleep(1)
                    self.SvcDoRun()
    
    def restart_service(self):
        try:
            subprocess.run(['sc', 'start', self._svc_name_], check=True, capture_output=True, text=True)
            servicemanager.LogInfoMsg(f"{self._svc_name_} service started.")
        except subprocess.CalledProcessError as e:
            servicemanager.LogErrorMsg(f"Error during restarting service: {str(e)}")
        except Exception as e:
            servicemanager.LogErrorMsg(f"Unexpected error: {str(e)}")


if __name__ == '__main__':
    HandleCommandLine(MyService)
