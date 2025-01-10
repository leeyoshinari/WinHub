#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import os
import sys
import subprocess
from win32serviceutil import ServiceFramework, HandleCommandLine
import win32service
import win32event


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
            self.process.terminate()  # 尝试优雅地终止进程
            self.process.wait()     # 等待进程结束

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        script_path = os.path.join(os.path.dirname(__file__), "main.py")
        self.process = subprocess.Popen([sys.executable, script_path])
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)


if __name__ == '__main__':
    HandleCommandLine(MyService)
