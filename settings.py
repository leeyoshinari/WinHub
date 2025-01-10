#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import os
import sys
import json
import configparser
import tzlocal


if hasattr(sys, 'frozen'):
    BASE_PATH = os.path.dirname(sys.executable)
else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
cfg = configparser.ConfigParser()
config_path = os.path.join(BASE_PATH, 'config.conf')
version_path = os.path.join(BASE_PATH, '__version__')
cfg.read(config_path, encoding='utf-8')
TOKENs = {}


def get_config(key):
    value = os.environ.get(key, None)
    if value is not None:
        return value
    return cfg.get('default', key, fallback="")


PREFIX = get_config("prefix")
HOST = get_config("host")
PORT = int(get_config("port"))
TRACKER_URL = get_config("trackerUrls")
ROOT_PATH = json.loads(get_config("rootPath"))
ENABLE_ONLYOFFICE = get_config("enableOnlyoffice")
ONLYOFFICE_SERVER = get_config("onlyOfficeServer")
ONLYOFFICE_SECRET = get_config("onlyOfficeSecret")
ONLYOFFICE_HISTORY_PATH = get_config("historyVersionPath")
ENABLE_BACKUP = int(get_config("enableBackup"))
BACKUP_PATH = get_config("backupPath")
BACKUP_INTERVAL = int(get_config("backupInterval"))
WEBRTC_STUN = get_config("STUN")
WEBRTC_TURN = get_config("TURN")
WEBRTC_USER = get_config("TURNUserName")
WEBRTC_CRED = get_config("credential")
LOGGER_LEVEL = get_config("level")
TMP_PATH = os.path.join(BASE_PATH, 'tmp')
KTV_TMP_PATH = os.path.join(TMP_PATH, 'ktv')
KARAOKE_PATH = os.path.join(ROOT_PATH['D'], 'karaoke_ktv')

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
    "timezone": str(tzlocal.get_localzone())
}

CONTENT_TYPE = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'bmp': 'image/bmp', 'png': 'image/png', 'pdf': 'application/pdf',
                'mp4': 'video/mp4', 'zip': 'application/zip', 'mp3': 'audio/mpeg', 'html': 'text/html', 'py': 'text/x-python',
                'txt': 'text/plain', 'json': 'application/json', 'sh': 'text/x-sh', 'js': 'text/javascript', 'css': 'text/css'}

HTML404 = """<!doctype html><html><head><title>Welcome to nginx!</title>
<style>body{width:35em;margin:0 auto;}</style></head><body><h1>Welcome to nginx!</h1>
<p>If you see this page, the nginx web server is successfully installed and working. Further configuration is required.</p><p>For online documentation and support please refer to nginx.org.<br>
Commercial support is available at nginx.com.</p><p><em>Thank you for using nginx.</em></p></body></html>"""
