#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import os
import sys
import json
import configparser

if hasattr(sys, 'frozen'):
    path = os.path.dirname(sys.executable)
else:
    path = os.path.dirname(os.path.abspath(__file__))
cfg = configparser.ConfigParser()
config_path = os.path.join(path, 'config.conf')
version_path = os.path.join(path, '__version__')
cfg.read(config_path, encoding='utf-8')
TOKENs = {}


def get_config(key):
    return cfg.get('default', key, fallback="")


TRACKER_URL = get_config("trackerUrls")
ROOT_PATH = json.loads(get_config("rootPath"))
TMP_PATH = os.path.join(path, 'tmp')
KTV_TMP_PATH = os.path.join(TMP_PATH, 'ktv')
KARAOKE_PATH = os.path.join(ROOT_PATH['D'], 'karaoke_ktv')
ENABLE_BACKUP = int(get_config("enableBackup"))
BACKUP_PATH = get_config("backupPath")
BACKUP_INTERVAL = int(get_config("backupInterval"))
WEBRTC_STUN = get_config("STUN")
WEBRTC_TURN = get_config("TURN")
WEBRTC_USER = get_config("TURNUserName")
WEBRTC_CRED = get_config("credential")

if not os.path.exists(TMP_PATH):
    os.mkdir(TMP_PATH)
if ENABLE_BACKUP == 1 and not os.path.exists(BACKUP_PATH):
    os.mkdir(BACKUP_PATH)
if not os.path.exists(KARAOKE_PATH):
    os.mkdir(KARAOKE_PATH)

with open(version_path, 'r') as f:
    SYSTEM_VERSION = float(f.read().strip().replace('v', ''))

TORTOISE_ORM = {
    "connections": {"default": get_config("dbUrl")},
    "apps": {
        "models": {
            "models": ["mycloud.models", "aerich.models"],
            "default_connection": "default"
        }
    },
    "timezone": "Asia/Shanghai"
}

CONTENT_TYPE = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'bmp': 'image/bmp', 'png': 'image/png', 'pdf': 'application/pdf',
                'mp4': 'video/mp4', 'zip': 'application/zip', 'mp3': 'audio/mpeg', 'html': 'text/html', 'py': 'text/x-python',
                'txt': 'text/plain', 'json': 'application/json', 'sh': 'text/x-sh', 'js': 'text/javascript', 'css': 'text/css'}

HTML404 = """<!doctype html><html><head><title>Welcome to nginx!</title>
<style>body{width:35em;margin:0 auto;}</style></head><body><h1>Welcome to nginx!</h1>
<p>If you see this page, the nginx web server is successfully installed and working. Further configuration is required.</p><p>For online documentation and support please refer to nginx.org.<br>
Commercial support is available at nginx.com.</p><p><em>Thank you for using nginx.</em></p></body></html>"""
