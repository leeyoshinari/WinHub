#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import os
import shutil
import traceback
from settings import ENABLE_BACKUP, ROOT_PATH, BACKUP_PATH, BACKUP_INTERVAL
from mycloud import models
from common.results import Result
from common.messages import Msg
from common.logging import logger
from common.scheduler import scheduler, get_schedule_time


async def start_backup(hh: models.SessionBase) -> Result:
    result = Result()
    if ENABLE_BACKUP != 1:
        result.code = 1
        result.msg = Msg.SyncDataNo.get_text(hh.lang)
        return result
    try:
        await start_sync(username=hh.username)
        result.msg = f'{Msg.SyncManual.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}'
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f'{Msg.SyncManual.get_text(hh.lang)} {Msg.Failure.get_text(hh.lang)}'
    return result


async def start_sync(username: str = None):
    folders = await models.Catalog.filter(is_backup=1)
    for folder in folders:
        folder_path = await folder.get_all_path()
        if username and f"/{username}" not in folder_path:
            continue
        for k, v in ROOT_PATH.items():
            if folder_path.startswith(v):
                relative_path = folder_path[len(v) + 1:]
                target_path = os.path.join(BACKUP_PATH, k, relative_path)
                if not os.path.exists(target_path):
                    os.makedirs(target_path, exist_ok=True)
                logger.info(f"Syncing {folder_path}")
                sync_data(folder_path, target_path)


async def index_backup(hh: models.SessionBase) -> Result:
    result = Result()
    if ENABLE_BACKUP != 1:
        result.code = 1
        result.msg = Msg.SyncDataNo.get_text(hh.lang)
        return result
    try:
        folders = await models.Catalog.filter(is_backup=1)
        folder_list = [models.FolderList.from_orm_format(f).model_dump() for f in folders if f.id.startswith(tuple('123456789')) and f"/{hh.username}" in await f.get_all_path()]
        result.data = folder_list
        result.total = len(result.data)
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
    return result


async def add_backup(folder_id: str, is_backup: int, hh: models.SessionBase) -> Result:
    result = Result()
    if ENABLE_BACKUP != 1:
        result.code = 1
        result.msg = Msg.SyncDataNo.get_text(hh.lang)
        return result
    try:
        is_backup = 1 if is_backup > 0 else 0
        folder = await models.Catalog.get(id=folder_id)
        folder.is_backup = is_backup
        await folder.save()
        result.msg = f"{Msg.Setting.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, folder_id, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f"{Msg.Setting.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
    return result


def sync_data(source_path: str, target_path: str):
    for root, dirs, files in os.walk(source_path):
        relative_path = os.path.relpath(root, source_path)
        target_root = os.path.join(target_path, relative_path)
        os.makedirs(target_root, exist_ok=True)
        for file in files:
            source_file = os.path.join(root, file)
            target_file = os.path.join(target_root, file)
            if not os.path.exists(target_file) or os.path.getmtime(source_file) > os.path.getmtime(target_file):
                shutil.copy2(source_file, target_file)

    for root, dirs, files in os.walk(target_path):
        relative_path = os.path.relpath(root, target_path)
        source_root = os.path.join(source_path, relative_path)
        for file in files:
            source_file = os.path.join(source_root, file)
            target_file = os.path.join(root, file)
            if not os.path.exists(source_file):
                os.remove(target_file)

        for d in dirs:
            source_dir = os.path.join(source_root, d)
            target_dir = os.path.join(root, d)
            if not os.path.exists(source_dir):
                shutil.rmtree(target_dir)


if ENABLE_BACKUP == 1:
    scheduler.add_job(start_sync, 'interval', days=BACKUP_INTERVAL, start_date=get_schedule_time())
