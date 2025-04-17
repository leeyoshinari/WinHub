#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

from litestar import Controller, get, post
from litestar.di import Provide
from mycloud import models
from mycloud.downloader import views
from mycloud.auth_middleware import auth
from common.results import Result


class DownloaderController(Controller):
    path = "/download"
    tags = ['downloader (下载器)']
    dependencies = {"hh": Provide(auth)}

    @get("/list", summary="Download file list (文件下载列表)")
    async def download_list_with_aria2c(self, hh: models.SessionBase) -> Result:
        result = await views.get_download_list(hh)
        return result

    @post("/file", summary="Download file (下载文件)")
    async def download_file_with_aria2c(self, data: models.DownloadFileOnline, hh: models.SessionBase) -> Result:
        if data.url.startswith("magnet:?"):
            result = await views.download_with_aria2c_bt(data, hh)
        elif ".m3u8" in data.url:
            result = await views.download_m3u8_video(data, hh)
        else:
            result = await views.download_with_aria2c_http(data, hh)
        return result

    @get("/torrent/open/{file_id: str}", summary="Download file")
    async def open_torrent(self, file_id: str, hh: models.SessionBase) -> Result:
        result = await views.open_torrent(file_id, hh)
        return result

    @post("/selected", summary="selected file (选择 BT 里的文件)")
    async def selected_bt(self, data: models.BtSelectedFiles, hh: models.SessionBase) -> Result:
        result = await views.download_selected_file(data, hh)
        return result

    @post("/status/update", summary="update download task status (更新下载任务的状态)")
    async def update_aria2c_status(self, data: models.DownloadFileOnlineStatus, hh: models.SessionBase) -> Result:
        result = await views.update_area2c_task_status(data, hh)
        return result
