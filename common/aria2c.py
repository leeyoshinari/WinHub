#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import time
import subprocess
import traceback
import requests
from settings import TRACKER_URL
from common.logging import logger


class Aria2Downloader:
    def __init__(self, aria2c_path='aria2c', rpc_port=6800):
        self.aria2c_path = aria2c_path
        self.rpc_port = rpc_port
        self.rpc_url = f'http://localhost:{rpc_port}/jsonrpc'
        self.process = None
        self.gid_dict = {}

    def start_rpc_server(self):
        self.process = subprocess.Popen([self.aria2c_path, '--enable-rpc=true', '--allow-overwrite=true', '--enable-dht=true', f'--dht-listen-port={self.rpc_port+2}', f'--rpc-listen-port={self.rpc_port}'])
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

    def add_gid_dict(self, gid: str, username: str):
        self.gid_dict.update({gid: username})

    def delete_gid_dict(self, gid: str):
        self.gid_dict.pop(gid)

    def add_http_task(self, url: str, file_path: str, file_name: str = "", cookie: str = ""):
        if not self.process:
            self.start_rpc_server()
            time.sleep(1)
        options = {
            "max-connection-per-server": "8",
            "split": "16",
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
        response = requests.post(self.rpc_url, json=payload, timeout=15)
        logger.info(response.json())
        return response.json().get('result')

    def add_bt_task(self, url: str, file_path: str):
        if not self.process:
            self.start_rpc_server()
            time.sleep(1)
        trackers = get_tracker_list()
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
        response = requests.post(self.rpc_url, json=payload, timeout=15)
        logger.info(response.json())
        return response.json().get('result')

    def add_bt_file(self, url: str, file_path: str):
        if not self.process:
            self.start_rpc_server()
            time.sleep(1)
        trackers = get_tracker_list()
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
        response = requests.post(self.rpc_url, json=payload, timeout=15)
        return response.json().get('result')

    def list_download_tasks(self, is_stop=True):
        payload = {
            "jsonrpc": "2.0",
            "method": "aria2.tellActive",
            "id": "2"
        }
        response = requests.post(self.rpc_url, json=payload, timeout=15)
        res = response.json().get('result', [])
        payload = {
            "jsonrpc": "2.0",
            "method": "aria2.tellWaiting",
            "id": "3",
            "params": [0, 100]
        }
        response = requests.post(self.rpc_url, json=payload, timeout=15)
        res += response.json().get('result', [])
        if is_stop:
            payload = {
                "jsonrpc": "2.0",
                "method": "aria2.tellStopped",
                "id": "30",
                "params": [0, 100]
            }
            response = requests.post(self.rpc_url, json=payload, timeout=15)
            res += response.json().get('result', [])
        return res

    def close_aria2c_downloader(self):
        if self.process:
            tasks = self.list_download_tasks(is_stop=False)
            if not tasks:
                self.stop_rpc_server()

    def get_completed_task_info(self, gid):
        payload = {
            "jsonrpc": "2.0",
            "method": "aria2.tellStatus",
            "id": "5",
            "params": [gid]
        }
        response = requests.post(self.rpc_url, json=payload, timeout=15)
        return response.json().get('result', {})

    def get_file_list(self, gid):
        payload = {
            "jsonrpc": "2.0",
            "method": "aria2.getFiles",
            "id": "8",
            "params": [gid]
        }
        response = requests.post(self.rpc_url, json=payload, timeout=15)
        return response.json().get('result', {})

    def select_files_to_download(self, gid, file_index):
        trackers = get_tracker_list()
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
        response = requests.post(self.rpc_url, json=payload, timeout=15)
        return response.json()

    def update_task(self, gid, method):
        methods = {'cancel': 'aria2.remove', 'continue': 'aria2.unpause', 'pause': 'aria2.pause', 'remove': 'aria2.removeDownloadResult'}
        payload = {
            "jsonrpc": "2.0",
            "method": methods[method],
            "id": "4",
            "params": [gid]
        }
        response = requests.post(self.rpc_url, json=payload, timeout=15)
        return response.json()


def get_tracker_list():
    urls = TRACKER_URL.split(',')
    tracker = []
    for url in urls:
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                lines = response.text.split('\n')
                tracker += [line for line in lines if len(line) > 3]
        except:
            logger.error(traceback.format_exc())
    logger.info(f"Tracker List: {tracker}")
    return ','.join(tracker)
