#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import time
import hashlib
import os.path
from common.messages import Msg


def str_md5(s: str):
    myhash = hashlib.md5()
    myhash.update(s.encode('utf-8'))
    return myhash.hexdigest()


def calc_md5(f):
    myhash = hashlib.md5()
    while True:
        b = f.read(8096)
        if not b:
            break
        myhash.update(b)
    return myhash.hexdigest()


def calc_file_md5(file_path: str):
    with open(file_path, 'rb') as f:
        res = calc_md5(f)
    return res


def time2date(timestamp: int) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))


def beauty_size(size: int) -> str:
    size = size / 1024
    if size < 1000:
        return f'{round(size, 2)} KB'
    else:
        size = size / 1024
    if size < 1000:
        return f'{round(size, 2)} MB'
    else:
        size = size / 1024
    if size < 1000:
        return f'{round(size, 2)} GB'
    else:
        return f'{round(size / 1024, 2)} TB'


def beauty_time(duration) -> str:
    minute, second = divmod(int(duration), 60)
    if minute < 60:
        return f"{minute:02}:{second:02}"
    elif minute < 1440:
        hour, minute = divmod(int(minute), 60)
        return f"{hour:02}:{minute:02}:{second:02}"
    else:
        hour, minute = divmod(int(minute), 60)
        day, hour = divmod(int(hour), 24)
        return f"{day}:{hour:02}:{minute:02}:{second:02}"


def beauty_time_pretty(time_list: list, format_str: str) -> str:
    length = len(time_list)
    res = ''
    if length == 0 or length > 4:
        return res
    if length == 4:
        res = format_str.format(time_list[0], time_list[1], time_list[2], time_list[3])
    if length == 3:
        res = format_str.format("-_-", time_list[0], time_list[1], time_list[2])
    if length == 2:
        res = format_str.format("", "-_-", time_list[0], time_list[1])
    if length == 1:
        res = format_str.format("", "", "-_-", time_list[0])
    res = res.split('-_-')[-1]
    return res


def beauty_mp3_time(duration) -> str:
    minute, second = divmod(int(duration), 60)
    return f"{minute:02}:{second:02}"


def beauty_chat_status(status: int, lang: str) -> str:
    return Msg.ChatStatus.get_text(lang)[status]


def beauty_chat_mode(mode: int, lang: str) -> str:
    return Msg.ChatMode.get_text(lang)[mode]


def modify_prefix(prefix='/mycloud'):
    if os.path.exists('web/head.js'):
        with open('web/head.js', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        lines[0] = f"const server = '{prefix}';\n"
        with open('web/head.js', 'w', encoding='utf-8') as f:
            f.writelines(lines)


def modify_sw():
    current_date = time.strftime("%Y-%m-%d-%H-%M-%S")
    if os.path.exists('web/sw.js'):
        with open('web/sw.js', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        lines[0] = f"const CACHE_NAME = 'winhub-{current_date}';\n"
        with open('web/sw.js', 'w', encoding='utf-8') as f:
            f.writelines(lines)


def modify_manifest(pwa_url):
    if os.path.exists('web/manifest.json'):
        with open('web/manifest.json', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        lines[4] = f'    "start_url": "{pwa_url}",\n'
        with open('web/manifest.json', 'w', encoding='utf-8') as f:
            f.writelines(lines)


def parse_pwd(password: str, s: str):
    p = ''
    time_len = len(s)
    for i in range(len(password)):
        if i < time_len:
            p += chr(ord(password[i]) ^ int(s[i]))
        else:
            p += chr(ord(password[i]) ^ int(s[i - time_len]))
    return p
