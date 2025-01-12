#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import os
import time
import json
import shutil
import zipfile
import subprocess
import traceback
import socket
import signal
import platform
import psutil
import requests
from mycloud import models
from settings import TMP_PATH, SYSTEM_VERSION, BASE_PATH, TIME_ZONE
from common.calc import beauty_time, beauty_size, beauty_time_pretty
from common.results import Result
from common.messages import Msg
from common.logging import logger


UPDATE_STATUE = 0   # 0-默认状态, 1-最新版本, 2-有新版本, 3-已更新,需要重启
NEWEST_VERSION = ''


async def get_system_info(hh: models.SessionBase) -> Result:
    result = Result()
    try:
        os_name = platform.system()  # 操作系统名称
        os_version = platform.version()  # 操作系统版本
        os_architecture = platform.architecture()[0].lower()  # 系统架构
        machine = platform.machine()
        logical_cores = psutil.cpu_count(logical=True)  # 逻辑核数
        uptime_seconds = time.time() - psutil.boot_time()
        cpu_run_time = beauty_time_pretty(beauty_time(uptime_seconds).split(':'), Msg.DateFormatPretty.get_text(hh.lang))  # 系统运行时间
        if os_name == "Windows":
            os_version = f"{os_name} {os_version}"
            os_processor = get_windows_cpu_model()
        elif os_name == "Darwin":
            os_version = os_version.split(":")[0].strip()
            os_processor = platform.processor()
        else:
            os_version = get_linux_system_version()
            os_processor = get_linux_cpu_model()
        total_memory = psutil.virtual_memory().total / 1073741824
        total_size = 0
        for partition in psutil.disk_partitions():
            disk_usage = psutil.disk_usage(partition.mountpoint)
            total_size += disk_usage.total
        result.data = {'os_name': os_name, 'os_version': os_version, 'cpu_core': logical_cores, 'memory': round(total_memory, 2),
                       'os_arch': os_architecture.replace('bit', ''), 'cpu_model': os_processor,
                       'disk': beauty_size(total_size), 'run_time': cpu_run_time, 'machine': machine}
        result.msg = f'{Msg.SystemInfo.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}'
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f'{Msg.SystemInfo.get_text(hh.lang)} {Msg.Failure.get_text(hh.lang)}'
    return result


async def get_resource(hh: models.SessionBase) -> Result:
    result = Result()
    try:
        virtual_memory = psutil.virtual_memory()
        initial_io = psutil.disk_io_counters()
        initial_net = psutil.net_io_counters()
        cpu_percent = psutil.cpu_percent(interval=1)
        final_io = psutil.disk_io_counters()
        final_net = psutil.net_io_counters()
        memory_percent = virtual_memory.percent
        total_memory = virtual_memory.total / 1073741824
        used_memory = virtual_memory.used / 1073741824
        available_memory = virtual_memory.available / 1073741824
        free_memory = virtual_memory.free / 1073741824
        io_read_bytes = (final_io.read_bytes - initial_io.read_bytes) / 1048576
        io_write_bytes = (final_io.write_bytes - initial_io.write_bytes) / 1048576
        net_sent_bytes = (final_net.bytes_sent - initial_net.bytes_sent) / 1048576
        net_recv_bytes = (final_net.bytes_recv - initial_net.bytes_recv) / 1048576
        result.data = {'cpu': round(cpu_percent, 2), 'memory_percent': round(memory_percent, 2),
                       'total_memory': round(total_memory, 2), 'used_memory': round(used_memory, 2),
                       'available_memory': round(available_memory, 2), 'free_memory': round(free_memory, 2),
                       'io_read': round(io_read_bytes, 2), 'io_write': round(io_write_bytes, 2),
                       'net_sent': round(net_sent_bytes, 2), 'net_recv': round(net_recv_bytes, 2)}
        result.msg = f'{Msg.SystemResource.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}'
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f'{Msg.SystemResource.get_text(hh.lang)} {Msg.Failure.get_text(hh.lang)}'
    return result


async def get_cpu_info(hh: models.SessionBase) -> Result:
    result = Result()
    try:
        logical_cores = psutil.cpu_count(logical=True)    # 逻辑核心数
        os_name = platform.system()
        if os_name == "Linux":
            cpu_model = get_linux_cpu_model()
        elif os_name == "Windows":
            cpu_model = get_windows_cpu_model()
        else:
            cpu_model = platform.processor()
        result.data = {'core': logical_cores, 'model': cpu_model}
        result.msg = f'{Msg.SystemCPUInfo.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}'
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f'{Msg.SystemCPUInfo.get_text(hh.lang)} {Msg.Failure.get_text(hh.lang)}'
    return result


async def get_disk_info(hh: models.SessionBase) -> Result:
    result = Result()
    try:
        total_size = 0
        used_size = 0
        for partition in psutil.disk_partitions():
            disk_usage = psutil.disk_usage(partition.mountpoint)
            total_size += disk_usage.total
            used_size += disk_usage.used
        result.data = {'total': beauty_size(total_size), 'used': beauty_size(used_size),
                       'usage': round(used_size / total_size * 100, 2)}
        result.msg = f'{Msg.SystemDiskInfo.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}'
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f'{Msg.SystemDiskInfo.get_text(hh.lang)} {Msg.Failure.get_text(hh.lang)}'
    return result


async def get_net_info(hh: models.SessionBase) -> Result:
    result = Result()
    try:
        net_speed = None
        net_name = ''
        ipv4_addr = ''
        ipv6_addr = ''
        mac_addr = ''
        network_interfaces = psutil.net_if_addrs()
        network_stats = psutil.net_if_stats()
        for interface_name, interface_addresses in network_interfaces.items():
            if "lo" in interface_name.lower():
                continue
            interface_status = network_stats[interface_name]
            if interface_status.isup:
                net_name = interface_name
                net_speed = f"{interface_status.speed} Mbps" if interface_status.speed else None
                for address in interface_addresses:
                    if address.family == socket.AF_INET:
                        ipv4_addr = address.address
                    elif address.family == socket.AF_INET6:
                        ipv6_addr = address.address
                    elif address.family == psutil.AF_LINK:
                        mac_addr = address.address
                break
        result.data = {'name': net_name, 'speed': net_speed, 'ipv4': ipv4_addr, 'ipv6': ipv6_addr, 'mac': mac_addr}
        result.msg = f'{Msg.SystemNetWorkInfo.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}'
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f'{Msg.SystemNetWorkInfo.get_text(hh.lang)} {Msg.Failure.get_text(hh.lang)}'
    return result


async def remove_tmp_folder(hh: models.SessionBase) -> Result:
    result = Result()
    try:
        for root, _, files in os.walk(TMP_PATH):
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                log_str = f"{Msg.Delete.get_text(hh.lang).format(file_path)}{Msg.Success.get_text(hh.lang)}"
                logger.info(Msg.CommonLog.get_text(hh.lang).format(log_str, hh.username, hh.ip))

        folders = os.listdir(TMP_PATH)
        for folder in folders:
            shutil.rmtree(os.path.join(TMP_PATH, folder))
            log_str = f"{Msg.Delete.get_text(hh.lang).format(folder)}{Msg.Success.get_text(hh.lang)}"
            logger.info(Msg.CommonLog.get_text(hh.lang).format(log_str, hh.username, hh.ip))
        result.msg = Msg.Delete.get_text(hh.lang).format('') + Msg.Success.get_text(hh.lang)
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = Msg.Delete.get_text(hh.lang) + Msg.Failure.get_text(hh.lang)
    return result


async def get_new_version(hh: models.SessionBase) -> Result:
    result = Result()
    global UPDATE_STATUE
    global NEWEST_VERSION
    try:
        res = requests.get("https://api.github.com/repos/leeyoshinari/WinHub/releases", timeout=30)
        if res.status_code == 200:
            res_json = json.loads(res.text)
            latest_version = float(res_json[0]['name'].replace('v', ''))
            current_version = float(SYSTEM_VERSION.replace('v', ''))
            body = []
            for v in res_json:
                body.append({'version': v['name'], 'publish_date': v['published_at'].split('T')[0], 'body': '<br>· '.join(parse_update_log(v['body']))})
            result.data = {'latest_version': res_json[0]['name'], 'current_version': SYSTEM_VERSION,
                           'is_new': current_version < latest_version, 'body': body, 'check_time': time.strftime("%Y-%m-%d %H:%M:%S")}
            UPDATE_STATUE = 2 if current_version < latest_version else 1
            NEWEST_VERSION = res_json[0]['name']
        result.msg = f"{Msg.SystemVersionInfo.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f"{Msg.SystemVersionInfo.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
    return result


async def update_system(hh: models.SessionBase) -> Result:
    result = Result()
    global UPDATE_STATUE
    global NEWEST_VERSION
    try:
        version = NEWEST_VERSION.replace('v', '')
        package_path = os.path.join(BASE_PATH, 'WinHub.zip')
        res = requests.get(f"https://github.com/leeyoshinari/WinHub/archive/refs/tags/{version}.zip", stream=True, timeout=3600)
        res.raise_for_status()
        with open(package_path, 'wb') as f:
            for chunk in res.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        result.msg = f"{Msg.SystemUpdateInfo.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        UPDATE_STATUE = 3
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f"{Msg.SystemUpdateInfo.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
    return result


async def restart_system(start_type: int, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        current_platform = platform.system().lower()
        if start_type == 1:
            package_path = os.path.join(BASE_PATH, 'WinHub.zip')
            if os.path.exists(package_path):
                tmp_name = 'WinHub-' + NEWEST_VERSION
                with zipfile.ZipFile(package_path, 'r') as f:
                    zip_files = f.namelist()
                    tmp_name = zip_files[0][: zip_files[0].index('/')]
                    f.extractall(BASE_PATH)
                origin_path = os.path.join(BASE_PATH, tmp_name)
                shutil.copytree(origin_path, BASE_PATH, dirs_exist_ok=True)
                shutil.rmtree(origin_path)
            # 安装第三方包
            time.sleep(1)
            if current_platform == "windows":
                pip_command = ["pip", "install", "-r", "requirements.txt"]
            else:
                pip_command = ["pip3", "install", "-r", "requirements.txt"]
            if TIME_ZONE == 'Asia/Shanghai':
                pip_command += ["-i", "https://pypi.tuna.tsinghua.edu.cn/simple", "--trusted-host", "pypi.tuna.tsinghua.edu.cn"]
            logger.info(f"Run pip command: {pip_command}, user: {hh.username}, IP: {hh.ip}")
            subprocess.run(pip_command, check=True, capture_output=True, text=True)

            # 更新数据库
            aerich_command = ["aerich", "migrate"]
            subprocess.run(aerich_command, check=True, capture_output=True, text=True)
            time.sleep(1)
            aerich_command = ["aerich", "upgrade"]
            subprocess.run(aerich_command, check=True, capture_output=True, text=True)
            logger.info(f"DataBase update, user: {hh.username}, IP: {hh.ip}")
        result.msg = f"{Msg.SystemRestartInfo.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
        if current_platform == "windows":
            subprocess.run(['sc', 'stop', 'WinHubService'], check=True, capture_output=True, text=True)
        else:
            os.kill(os.getppid(), signal.SIGHUP)
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f"{Msg.SystemRestartInfo.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
    return result


def get_update_status():
    return UPDATE_STATUE


def get_windows_cpu_model() -> str:
    try:
        result = subprocess.run(['wmic', 'cpu', 'get', 'name'], capture_output=True, text=True, check=True)
        return result.stdout.replace('Name', '').strip()
    except:
        logger.error(traceback.format_exc())
        return ''


def get_linux_cpu_model() -> str:
    try:
        res = exec_cmd('cat /proc/cpuinfo |grep "model name"')
        cpu_model = res[0].split(':')[-1].strip()
        return cpu_model
    except:
        logger.error(traceback.format_exc())
        return ''


def get_linux_system_version() -> str:
    try:
        result = exec_cmd("cat /etc/os-release |grep PRETTY_NAME | awk '{print$1}' |awk -F '=' '{print $2}'")[0]
        version = exec_cmd("cat /etc/os-release |grep VERSION_ID |awk -F '=' '{print $2}'")[0]
        system_name = result.strip().replace('"', '')
        system_version = version.strip().replace('"', '')
        result = f"{system_name} {system_version}"
    except:
        logger.warning(traceback.format_exc())
        system_a = exec_cmd('uname -s')[0]  # system kernel version
        system_r = exec_cmd('uname -r')[0]
        result = f"{system_a.strip()} {system_r.strip()}"
    return result


def parse_update_log(log_str: str):
    result = []
    try:
        changed_str = log_str.split('##')[1]
        result = changed_str.split('*')[1:]
    except:
        logger.error(traceback.format_exc)
    if len(result) > 0:
        result[0] = '· ' + result[0]
    return result


def exec_cmd(cmd):
    with os.popen(cmd) as p:
        res = p.readlines()
    return res
