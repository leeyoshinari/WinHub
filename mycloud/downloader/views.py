#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import os
import shutil
import time
import base64
import asyncio
import subprocess
import threading
import traceback
from urllib.parse import urlparse
from settings import TMP_PATH
from mycloud import models
from common.results import Result
from common.messages import Msg
from common.logging import logger
from common.calc import calc_file_md5
from common.aria2c import Aria2Downloader


aria2c_downloader = Aria2Downloader()


async def get_download_list(hh: models.SessionBase) -> Result:
    result = Result()
    try:
        if not aria2c_downloader.process:
            result.data = []
            return result
        file_lists = aria2c_downloader.list_download_tasks()
        download_list = [models.DownloadList.from_orm_format(d).model_dump() for d in file_lists if aria2c_downloader.gid_dict.get(d['gid'], '') == hh.username]
        result.data = download_list
        result.total = len(download_list)
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def download_with_aria2c_http(query: models.DownloadFileOnline, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        folder_id = query.parent_id
        if len(folder_id) == 1:
            folder_id = folder_id + hh.username
        if len(folder_id) <= 3:
            result.code = 1
            result.msg = Msg.AccessPermissionNon.get_text(hh.lang)
            return result
        file_path = TMP_PATH
        gid = aria2c_downloader.add_http_task(query.url, TMP_PATH, query.file_name, query.cookie)
        res = aria2c_downloader.get_completed_task_info(gid)
        completed_length = res['completedLength']
        start_time = time.time()
        while res['completedLength'] == completed_length:
            logger.info(res)
            if 'errorCode' in res:
                if res['status'] == 'complete':
                    file_path = res['files'][0]['path']
                    result.msg = Msg.FileExist.get_text(hh.lang).format(file_path.split('/')[-1])
                    logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, query.url, hh.username, hh.ip))
                    aria2c_downloader.close_aria2c_downloader()
                    return result
                if res['errorCode'] == '1' and not res['files'][0]['path'] and not res['files'][0]['uris']:
                    result.code = 1
                    result.msg = Msg.DownloadOnlineProtocol.get_text(hh.lang)
                    logger.error(Msg.CommonLog1.get_text(hh.lang).format(res, query.url, hh.username, hh.ip))
                    aria2c_downloader.close_aria2c_downloader()
                    return result
                result.code = 1
                result.msg = res['errorMessage']
                logger.error(Msg.CommonLog1.get_text(hh.lang).format(res, query.url, hh.username, hh.ip))
                aria2c_downloader.close_aria2c_downloader()
                return result
            else:
                if time.time() - start_time > 30:
                    result.code = 1
                    result.msg = Msg.DownloadOnlineProtocol.get_text(hh.lang)
                    logger.error(Msg.CommonLog1.get_text(hh.lang).format(result.msg, query.url, hh.username, hh.ip))
                    _ = aria2c_downloader.update_task(gid, 'cancel')
                    time.sleep(2)
                    _ = aria2c_downloader.update_task(gid, 'remove')
                    time.sleep(2)
                    aria2c_downloader.close_aria2c_downloader()
                    return result
                time.sleep(1)
                res = aria2c_downloader.get_completed_task_info(gid)
        threading.Thread(target=run_async_write_aria2c_to_db, args=(gid, folder_id, )).start()
        aria2c_downloader.add_gid_dict(gid, hh.username)
        result.msg = Msg.DownloadOnline.get_text(hh.lang)
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(query.url, gid, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = Msg.DownloadError.get_text(hh.lang)
        logger.error(traceback.format_exc())
    return result


async def download_with_aria2c_bt(query: models.DownloadFileOnline, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        folder_id = query.parent_id
        if len(folder_id) == 1:
            folder_id = folder_id + hh.username
        if len(folder_id) <= 3:
            result.code = 1
            result.msg = Msg.AccessPermissionNon.get_text(hh.lang)
            return result
        gid = aria2c_downloader.add_bt_task(query.url, TMP_PATH)
        res = aria2c_downloader.get_completed_task_info(gid)
        while res['status'] != 'complete':
            logger.info(res)
            time.sleep(1)
            res = aria2c_downloader.get_completed_task_info(gid)
        res = aria2c_downloader.get_completed_task_info(gid)
        new_gid = res['followedBy'][0]
        file_list = aria2c_downloader.get_file_list(new_gid)
        aria2c_downloader.update_task(new_gid, 'pause')
        bt_file_list = [models.BtFileList.from_orm_format(f, new_gid, folder_id).model_dump() for f in file_list if int(f['length']) > 1024]
        aria2c_downloader.update_task(gid, "remove")
        aria2c_downloader.add_gid_dict(new_gid, hh.username)
        result.data = bt_file_list
        result.total = len(result.data)
        result.msg = Msg.DownloadOnline.get_text(hh.lang)
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(query.url, gid, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = Msg.DownloadError.get_text(hh.lang)
        logger.error(traceback.format_exc())
    return result


async def open_torrent(file_id: str, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        file = await models.Files.get(id=file_id).select_related('parent')
        folder_path = await file.parent.get_all_path()
        gid = aria2c_downloader.add_bt_file(base64.b64encode(open(os.path.join(folder_path, file.name), 'rb').read()).decode('ascii'), TMP_PATH)
        res = aria2c_downloader.get_completed_task_info(gid)
        new_gid = res['gid']
        file_list = aria2c_downloader.get_file_list(new_gid)
        aria2c_downloader.update_task(new_gid, 'pause')
        bt_file_list = [models.BtFileList.from_orm_format(f, new_gid, file.parent_id).model_dump() for f in file_list if int(f['length']) > 1024]
        aria2c_downloader.add_gid_dict(new_gid, hh.username)
        aria2c_downloader.update_task(gid, "remove")
        result.data = bt_file_list
        result.total = len(result.data)
        result.msg = Msg.DownloadOnline.get_text(hh.lang)
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(file.name, gid, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = Msg.DownloadOnlineProtocol.get_text(hh.lang)
    return result


def run_async_write_aria2c_to_db(gid, parent_id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(write_aria2c_task_to_db(gid, parent_id))
    except:
        logger.error(traceback.format_exc())
    finally:
        loop.close()


async def write_aria2c_task_to_db(gid, parent_id):
    while True:
        try:
            res = aria2c_downloader.get_completed_task_info(gid)
            files = [r for r in res['files'] if r['selected'] == 'true']
            if files and files[0]['completedLength'] == files[0]['length']:
                file_path = files[0]['path']
                file_name = os.path.basename(file_path)
                folder = await models.Catalog.get(id=parent_id)
                folder_path = await folder.get_all_path()
                file = await models.Files.create(id=str(int(time.time() * 10000)), name=file_name,
                                                 format=file_name.split(".")[-1].lower(), parent_id=parent_id,
                                                 size=os.path.getsize(file_path), md5=calc_file_md5(file_path))
                shutil.move(file_path, folder_path)
                logger.info(f"{file.id} - {file.name}")
                aria2c_downloader.update_task(gid, "cancel")
                aria2c_downloader.delete_gid_dict(gid)
                time.sleep(2)
                aria2c_downloader.update_task(gid, "remove")
                time.sleep(3)
                aria2c_downloader.close_aria2c_downloader()
                break
            elif not files:
                logger.info(res)
                break
            else:
                logger.info(f"{res['gid']} - {res['status']} - {files[0]['completedLength']} - {files[0]['length']}")
                time.sleep(1)
        except:
            logger.error(traceback.format_exc())
            aria2c_downloader.update_task(gid, "remove")
            time.sleep(3)
            aria2c_downloader.close_aria2c_downloader()
            break


async def update_area2c_task_status(query: models.DownloadFileOnlineStatus, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        status_list = query.status.split(',')
        for s in status_list:
            res = aria2c_downloader.update_task(query.gid, s)
            if s in ['remove', 'cancel']:
                time.sleep(1)
                aria2c_downloader.delete_gid_dict(query.gid)
                aria2c_downloader.close_aria2c_downloader()
                break
            result.data = res
        result.msg = Msg.UpdateStatus.get_text(hh.lang)
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, query.gid, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
    return result


async def download_selected_file(query: models.BtSelectedFiles, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        res = aria2c_downloader.select_files_to_download(query.gid, query.index)
        logger.info(res)
        if 'result' in res and res['result'] == 'OK':
            res = aria2c_downloader.update_task(query.gid, "continue")
        else:
            result.code = 1
            result.msg = res['error']["message"]
            logger.error(f"{Msg.DownloadError.get_text(hh.lang)}, gid: {query.gid}, username: {hh.username}, ip: {hh.ip}")
            return result
        threading.Thread(target=run_async_write_aria2c_to_db, args=(query.gid, query.folder,)).start()
        result.msg = Msg.DownloadOnline.get_text(hh.lang)
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(query.gid, query.index, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = Msg.DownloadError.get_text(hh.lang)
        logger.error(traceback.format_exc())
    return result


async def download_m3u8_video(query: models.DownloadFileOnline, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        url_parse = urlparse(query.url)
        if query.file_name:
            file_name = os.path.join(TMP_PATH, query.file_name)
        else:
            file_name = os.path.join(TMP_PATH, f"{url_parse.path[1:].replace('/', '-')}.mp4")
        cmd = ['ffmpeg', '-i', query.url, '-c', 'copy', file_name]
        if query.cookie:
            cmd = ['ffmpeg', '-headers', f'Cookie: {query.cookie}', '-i', query.url, '-c', 'copy', file_name]
        threading.Thread(target=run_async_write_m3u8_to_db, args=(cmd, query.parent_id, file_name,)).start()
        result.msg = Msg.Download.get_text(hh.lang).format(file_name.replace(TMP_PATH, ''))
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, query.parent_id, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = Msg.Download.get_text(hh.lang)
    return result


def run_async_write_m3u8_to_db(cmd, parent_id, file_name):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(write_m3u8_task_to_db(cmd, parent_id, file_name))
    except:
        logger.error(traceback.format_exc())
    finally:
        loop.close()


async def write_m3u8_task_to_db(cmd, parent_id, file_path):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    while True:
        try:
            output = process.stderr.readline()
            if output == '' and process.poll() is not None:
                break
            logger.info(output)
        except:
            logger.error(traceback.format_exc())
            break

    process.wait()
    if process.returncode == 0:
        file_name = os.path.basename(file_path)
        folder = await models.Catalog.get(id=parent_id)
        folder_path = await folder.get_all_path()
        file = await models.Files.create(id=str(int(time.time() * 10000)), name=file_name,
                                         format=file_name.split(".")[-1].lower(), parent_id=parent_id,
                                         size=os.path.getsize(file_path), md5=calc_file_md5(file_path))
        shutil.move(file_path, folder_path)
        logger.info(f"Download m3u8 completed successfully! fileId: {file.id}, fileName: {file.name}")
    else:
        logger.info(f"Download m3u8 failed with error code: {process.returncode}, fileName: {file_path}")
