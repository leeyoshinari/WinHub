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
from settings import TMP_PATH, BASE_PATH, TIME_ZONE, ENABLED_AUTO_UPDATE, PIP_CMD, AERICH_CMD
from common.calc import beauty_time, beauty_size, beauty_time_pretty
from common.scheduler import scheduler, get_schedule_time
from common.results import Result
from common.messages import Msg
from common.logging import logger


UPDATE_STATUE = 0   # 0-默认状态, 1-最新版本, 2-有新版本, 3-已更新,需要重启
UPDATE_DATE_PATH = os.path.join(BASE_PATH, '__update_date__')


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
    try:
        res = requests.get("https://api.github.com/repos/leeyoshinari/WinHub/releases/latest", timeout=30)
        if res.status_code == 200:
            res_json = json.loads(res.text)
            latest_version = res_json['name']
            current_version = ""
            if os.path.exists(UPDATE_DATE_PATH):
                with open(UPDATE_DATE_PATH, 'r') as f:
                    update_info = f.read()
                current_version = update_info.split('_')[0]
            UPDATE_STATUE = 1 if current_version == latest_version else 2
            with open(UPDATE_DATE_PATH, 'w') as f:
                f.write(f'{current_version}_{time.strftime("%Y-%m-%d %H:%M:%S")}')
            result.data = {'zip_url': res_json['zipball_url'], 'status': UPDATE_STATUE, 'check_time': time.strftime("%Y-%m-%d %H:%M:%S"), 'name': latest_version}
        result.msg = f"{Msg.SystemVersionInfo.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f"{Msg.SystemVersionInfo.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
    return result


async def get_version_log(hh: models.SessionBase) -> Result:
    result = Result()
    try:
        res = requests.get("https://api.github.com/repos/leeyoshinari/WinHub/releases", timeout=30)
        if res.status_code == 200:
            res_json = json.loads(res.text)
            body = []
            for v in res_json:
                body.append({'version': v['name'], 'publish_date': v['published_at'].split('T')[0], 'body': '<br>· '.join(parse_update_log(v['body']))})
            result.data = body
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
    try:
        update_info_res = await get_new_version(hh)
        zip_url = update_info_res.data['zip_url'] if update_info_res.data else ""
        package_path = os.path.join(BASE_PATH, 'WinHub.zip')
        res = requests.get(zip_url, stream=True, timeout=3600)
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
                windows_cmd = PIP_CMD
                if PIP_CMD.startswith("pip"):
                    if PIP_CMD == 'pip3':
                        windows_cmd = 'pip'
                pip_command = [windows_cmd, "install", "-r", "requirements.txt"]
            else:
                pip_command = [PIP_CMD, "install", "-r", "requirements.txt"]
            if TIME_ZONE == 'Asia/Shanghai':
                pip_command += ["-i", "https://mirrors.ustc.edu.cn/pypi/simple/", "--trusted-host", "mirrors.ustc.edu.cn"]
            logger.info(f"Run pip command: {pip_command}, user: {hh.username}, IP: {hh.ip}")
            subprocess.run(pip_command, check=True, capture_output=True, text=True, timeout=60)

            # 更新数据库
            aerich_command = [AERICH_CMD, "migrate"]
            subprocess.run(aerich_command, check=True, capture_output=True, text=True, timeout=15)
            time.sleep(1)
            aerich_command = [AERICH_CMD, "upgrade"]
            subprocess.run(aerich_command, check=True, capture_output=True, text=True, timeout=15)
            logger.info(f"DataBase update, user: {hh.username}, IP: {hh.ip}")

            update_info_res = await get_new_version(hh)
            newest_version = update_info_res.data['name'] if update_info_res.data else ""
            with open(UPDATE_DATE_PATH, 'w') as f:
                f.write(f'{newest_version}_{time.strftime("%Y-%m-%d %H:%M:%S")}')
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


async def auto_update():
    try:
        hh = models.SessionBase(username='system', lang='en', ip='127.0.0.1')
        version = await get_new_version(hh)
        if version.code == 0 and version.data['status'] == 2:
            result = await update_system(hh)
            if result.code == 0:
                result = await restart_system(1, hh)
                logger.info(f"{Msg.SystemUpdateInfo.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}, username: {hh.username}, result: {result.msg}")
    except:
        logger.error(traceback.format_exc())


def get_update_status(hh: models.SessionBase):
    update_date = ''
    if os.path.exists(UPDATE_DATE_PATH):
        with open(UPDATE_DATE_PATH, 'r') as f:
            update_date = f.read()
    logger.info(f"Get system status, username: {hh.username}, ip: {hh.ip}")
    return {'status': UPDATE_STATUE, 'date': update_date.split('_')[-1]}


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
        result = log_str.split('- ')[1:]
    except:
        logger.error(traceback.format_exc())
    if len(result) > 0:
        result[0] = '· ' + result[0]
    return result


def exec_cmd(cmd):
    with os.popen(cmd) as p:
        res = p.readlines()
    return res


if ENABLED_AUTO_UPDATE == 1:
    scheduler.add_job(auto_update, 'interval', days=1, start_date=get_schedule_time(hour=5, minute=30))     # 自动更新的时间需要和其他任务的时间分开
