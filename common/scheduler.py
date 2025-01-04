#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import os
import time
import shutil
import datetime
import traceback
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from common.logging import logger
from settings import TMP_PATH


scheduler = AsyncIOScheduler()


def remove_tmp_folder():
    try:
        # 删除最近30分钟没有修改的文件，避免删除当前正在编辑的文件
        for root, dirs, files in os.walk(TMP_PATH):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.getmtime(file_path) < time.time() - 1800:
                    os.remove(file_path)
                    logger.info(f"Delete file successfully. file: {file_path}")

        # 删除文件后，再删除目录。如果目录大于 1KB，说明该目录正在使用，不删除
        folders = os.listdir(TMP_PATH)
        for folder in folders:
            if get_folder_size(folder) < 1024:
                shutil.rmtree(os.path.join(TMP_PATH, folder))
                logger.info(f"Remove directory successfully. folder: {folder}")
    except:
        logger.error(traceback.format_exc())


def get_folder_size(folder_path) -> int:
    total_size = 0
    for root, dirs, files in os.walk(folder_path):
        try:
            for file in files:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
                if total_size > 2048:
                    return total_size
        except:
            continue
    return total_size


def get_schedule_time():
    hour = 5
    minute = 20
    second = 20
    now = datetime.datetime.now()
    scheduled_time = now.replace(hour=hour, minute=minute, second=second, microsecond=0)
    if now < scheduled_time:
        return scheduled_time
    else:
        tomorrow = now + datetime.timedelta(days=1)
        return tomorrow.replace(hour=hour, minute=minute, second=second, microsecond=0)


scheduler.add_job(remove_tmp_folder, 'cron', hour=5, minute=20, second=21)
