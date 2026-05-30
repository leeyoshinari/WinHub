#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import os
import json
import asyncio
import subprocess
import traceback
import platform
from settings import TRACKER_URL
from common.httpRequest import HttpClient
from common.logging import logger


class Aria2Downloader:
    def __init__(self, aria2c_path='aria2c', rpc_port=6800):
        self.aria2c_path = aria2c_path
        self.rpc_port = rpc_port
        self.rpc_url = f'http://localhost:{rpc_port}/jsonrpc'
        self.process = None
        self.session = None
        self.gid_dict = {}
        self.kill_aria2c()

    def get_session(self):
        if self.session is None:
            self.session = HttpClient()
        return self.session

    def start_rpc_server(self):
        self.process = subprocess.Popen([self.aria2c_path, '--enable-rpc=true', '--allow-overwrite=true', '--enable-dht=true', f'--dht-listen-port={self.rpc_port + 2}', f'--rpc-listen-port={self.rpc_port}'])
        logger.info('aria2c RPC server started.')

    def stop_rpc_server(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
            self.gid_dict = {}
            logger.info('aria2c RPC server stopped.')
        else:
            logger.info('aria2c RPC server has stopped.')

    def kill_aria2c(self):
        try:
            current_platform = platform.system().lower()
            if current_platform == "windows":
                stop_cmd = "tasklist | findstr aria2c.exe"
                result = subprocess.run(stop_cmd, capture_output=True, text=True, shell=True, timeout=15)
                if result.stdout:
                    stop_cmd = ["taskkill", "/F", "/IM", "aria2c.exe"]
                    subprocess.run(stop_cmd, check=True, capture_output=True, text=True, timeout=15)
            else:
                stop_cmd = "ps -ef|grep aria2c|grep -v grep"
                with os.popen(stop_cmd) as p:
                    result = p.read()
                if result:
                    stop_cmd = "ps -ef|grep aria2c|grep -v grep |awk '{print $2}' |xargs kill -9"
                    with os.popen(stop_cmd) as p:
                        _ = p.read()
        except:
            logger.error(traceback.format_exc())

    def add_gid_dict(self, gid: str, username: str):
        self.gid_dict.update({gid: username})

    def delete_gid_dict(self, gid: str):
        self.gid_dict.pop(gid)

    async def add_http_task(self, url: str, file_path: str, file_name: str = "", cookie: str = ""):
        if not self.process:
            self.start_rpc_server()
            await asyncio.sleep(1)
        options = {
            "max-connection-per-server": "8",
            "split": "8",
            "continue": "true",
            "dir": file_path
        }
        if cookie:
            options["header"] = "Cookie:" + cookie
        if file_name:
            options["out"] = file_name
        payload = {
            "jsonrpc": "2.0",
            "method": "aria2.addUri",
            "id": "1",
            "params": [[url], options]
        }
        http = self.get_session()
        response = await http.post(self.rpc_url, json=payload, timeout=15)
        logger.info(response.text)
        return json.loads(response.text).get('result')

    async def add_bt_task(self, url: str, file_path: str):
        if not self.process:
            self.start_rpc_server()
            await asyncio.sleep(1)
        trackers = await get_tracker_list()
        options = {
            "max-connection-per-server": "8",
            "split": "8",
            "continue": "true",
            "bt.metadataOnly": "true",
            "dir": file_path
        }
        if trackers:
            options["bt-tracker"] = trackers
        payload = {
            "jsonrpc": "2.0",
            "method": "aria2.addUri",
            "id": "1",
            "params": [[url], options]
        }
        http = self.get_session()
        response = await http.post(self.rpc_url, json=payload, timeout=15)
        logger.info(response.text)
        return json.loads(response.text).get('result')

    async def add_bt_file(self, url: str, file_path: str):
        if not self.process:
            self.start_rpc_server()
            await asyncio.sleep(1)
        trackers = await get_tracker_list()
        options = {
            "max-connection-per-server": "8",
            "split": "8",
            "continue": "true",
            "bt.metadataOnly": "true",
            "dir": file_path
        }
        if trackers:
            options["bt-tracker"] = trackers
        payload = {
            "jsonrpc": "2.0",
            "method": "aria2.addTorrent",
            "id": "1",
            "params": [url, [], options]
        }
        http = self.get_session()
        response = await http.post(self.rpc_url, json=payload, timeout=15)
        return json.loads(response.text).get('result')

    async def list_download_tasks(self, is_stop=True):
        payload = {
            "jsonrpc": "2.0",
            "method": "aria2.tellActive",
            "id": "2"
        }
        http = self.get_session()
        response = await http.post(self.rpc_url, json=payload, timeout=15)
        res = json.loads(response.text).get('result', [])
        payload = {
            "jsonrpc": "2.0",
            "method": "aria2.tellWaiting",
            "id": "3",
            "params": [0, 100]
        }
        response = await http.post(self.rpc_url, json=payload, timeout=15)
        res += json.loads(response.text).get('result', [])
        if is_stop:
            payload = {
                "jsonrpc": "2.0",
                "method": "aria2.tellStopped",
                "id": "30",
                "params": [0, 100]
            }
            response = await http.post(self.rpc_url, json=payload, timeout=15)
            res += json.loads(response.text).get('result', [])
        return res

    async def close_aria2c_downloader(self):
        if self.process:
            tasks = await self.list_download_tasks(is_stop=False)
            if not tasks:
                self.stop_rpc_server()

    async def get_completed_task_info(self, gid):
        payload = {
            "jsonrpc": "2.0",
            "method": "aria2.tellStatus",
            "id": "5",
            "params": [gid]
        }
        http = self.get_session()
        response = await http.post(self.rpc_url, json=payload, timeout=15)
        return json.loads(response.text).get('result', {})

    async def get_file_list(self, gid):
        payload = {
            "jsonrpc": "2.0",
            "method": "aria2.getFiles",
            "id": "8",
            "params": [gid]
        }
        http = self.get_session()
        response = await http.post(self.rpc_url, json=payload, timeout=15)
        return json.loads(response.text).get('result', {})

    async def select_files_to_download(self, gid, file_index):
        trackers = await get_tracker_list()
        options = {
            "max-connection-per-server": "8",
            "split": "8",
            "continue": "true",
            "select-file": f"{file_index}"
        }
        if trackers:
            options["bt-tracker"] = trackers
        payload = {
            "jsonrpc": "2.0",
            "id": "9",
            "method": "aria2.changeOption",
            "params": [gid, options]  # {"select-file": f"{file_index}"}]
        }
        http = self.get_session()
        response = await http.post(self.rpc_url, json=payload, timeout=15)
        return json.loads(response.text)

    async def update_task(self, gid, method):
        methods = {'cancel': 'aria2.remove', 'continue': 'aria2.unpause', 'pause': 'aria2.pause', 'remove': 'aria2.removeDownloadResult'}
        payload = {
            "jsonrpc": "2.0",
            "method": methods[method],
            "id": "4",
            "params": [gid]
        }
        http = self.get_session()
        response = await http.post(self.rpc_url, json=payload, timeout=15)
        return json.loads(response.text)


async def get_tracker_list():
    urls = TRACKER_URL.split(',')
    tracker = []
    http = HttpClient()
    for url in urls:
        try:
            response = await http.get(url, timeout=15)
            if response.status_code == 200:
                lines = response.text.split('\n')
                tracker += [line for line in lines if len(line) > 3]
        except:
            logger.error(traceback.format_exc())
    logger.info(f"Tracker List: {tracker}")
    del http
    return ','.join(tracker)
