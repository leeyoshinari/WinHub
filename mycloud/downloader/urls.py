#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

from fastapi import APIRouter, Depends
from mycloud import models
from mycloud.downloader import views
from mycloud.auth_middleware import auth


router = APIRouter(prefix='/download', tags=['downloader (下载器)'], responses={404: {'description': 'Not found'}})


@router.get("/list", summary="Download file list (文件下载列表)")
async def download_list_with_aria2c(hh: models.SessionBase = Depends(auth)):
    result = await views.get_download_list(hh)
    return result


@router.post("/file", summary="Download file (下载文件)")
async def download_file_with_aria2c(query: models.DownloadFileOnline, hh: models.SessionBase = Depends(auth)):
    if query.url.startswith("magnet:?"):
        result = await views.download_with_aria2c_bt(query, hh)
    elif ".m3u8" in query.url:
        result = await views.download_m3u8_video(query, hh)
    else:
        result = await views.download_with_aria2c_http(query, hh)
    return result


@router.get("/torrent/open/{file_id}", summary="Download file")
async def open_torrent(file_id: str, hh: models.SessionBase = Depends(auth)):
    result = await views.open_torrent(file_id, hh)
    return result


@router.post("/selected", summary="selected file (选择 BT 里的文件)")
async def selected_bt(query: models.BtSelectedFiles, hh: models.SessionBase = Depends(auth)):
    result = await views.download_selected_file(query, hh)
    return result


@router.post("/status/update", summary="update download task status (更新下载任务的状态)")
async def update_aria2c_status(query: models.DownloadFileOnlineStatus, hh: models.SessionBase = Depends(auth)):
    result = await views.update_area2c_task_status(query, hh)
    return result
