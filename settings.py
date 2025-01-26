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


FRONT_END_PREFIX = get_config("winHubFrontEndPrefix")
PREFIX = get_config("winHubBackEndPrefix")
HOST = get_config("winHubHost")
PORT = int(get_config("winHubPort"))
TRACKER_URL = get_config("winHubTrackerUrls")
ROOT_PATH = json.loads(get_config("winHubRootPath"))
PWA_URL = get_config("winHubPwaUrl")
ENABLE_ONLYOFFICE = get_config("winHubEnableOnlyoffice")
ONLYOFFICE_SERVER = get_config("winHubOnlyOfficeServer")
ONLYOFFICE_SECRET = get_config("winHubOnlyOfficeSecret")
ONLYOFFICE_HISTORY_PATH = get_config("winHubHistoryVersionPath")
ENABLE_BACKUP = int(get_config("winHubEnableBackup"))
BACKUP_PATH = get_config("winHubBackupPath")
BACKUP_INTERVAL = int(get_config("winHubBackupInterval"))
ENABLED_AUTO_UPDATE = int(get_config("winHubEnabledAutoUpdate"))
WEBRTC_STUN = get_config("winHubSTUN")
WEBRTC_TURN = get_config("winHubTURN")
WEBRTC_USER = get_config("winHubTURNUserName")
WEBRTC_CRED = get_config("winHubCredential")
LOGGER_LEVEL = get_config("winHubLevel")
PIP_CMD = get_config("winHubPipCmd")
AERICH_CMD = get_config("winHubAerichCmd")
TMP_PATH = os.path.join(BASE_PATH, 'tmp')
KTV_TMP_PATH = os.path.join(TMP_PATH, 'ktv')
KARAOKE_PATH = os.path.join(ROOT_PATH['D'], 'karaoke_ktv')
TIME_ZONE = str(tzlocal.get_localzone())

if not os.path.exists(TMP_PATH):
    os.mkdir(TMP_PATH)
if ENABLE_BACKUP == 1 and not os.path.exists(BACKUP_PATH):
    os.mkdir(BACKUP_PATH)
if not os.path.exists(KARAOKE_PATH):
    os.mkdir(KARAOKE_PATH)

with open(version_path, 'r') as f:
    SYSTEM_VERSION = f.read().strip()

TORTOISE_ORM = {
    "connections": {"default": get_config("winHubDbUrl")},
    "apps": {
        "models": {
            "models": ["mycloud.models", "aerich.models"],
            "default_connection": "default"
        }
    },
    "timezone": TIME_ZONE
}

CONTENT_TYPE = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'bmp': 'image/bmp', 'png': 'image/png', 'pdf': 'application/pdf',
                'mp4': 'video/mp4', 'zip': 'application/zip', 'mp3': 'audio/mpeg', 'html': 'text/html', 'py': 'text/x-python',
                'txt': 'text/plain', 'json': 'application/json', 'sh': 'text/x-sh', 'js': 'text/javascript', 'css': 'text/css'}

HTML404 = """<!doctype html><html><head><title>Welcome to nginx!</title>
<style>body{width:35em;margin:0 auto;}</style></head><body><h1>Welcome to nginx!</h1>
<p>If you see this page, the nginx web server is successfully installed and working. Further configuration is required.</p><p>For online documentation and support please refer to nginx.org.<br>
Commercial support is available at nginx.com.</p><p><em>Thank you for using nginx.</em></p></body></html>"""
