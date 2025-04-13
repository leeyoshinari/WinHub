#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

from litestar import Controller, get, post
from litestar.di import Provide
from mycloud import models
from mycloud.folders import views
from mycloud.auth_middleware import auth
from common.results import Result


class FolderController(Controller):
    path = "/folder"
    tags = ['folder (文件夹)']
    dependencies = {"hh": Provide(auth)}

    @get("/getDisk", summary="Get disk usage (获取磁盘空间使用数据)")
    async def get_disk_info(self, hh: models.SessionBase) -> Result:
        result = await views.get_disk_usage(hh)
        return result

    @get('/get/{file_id: str}', summary="Query all folders in the current directory (查询当前目录下所有的文件夹)")
    async def get_folder_name(self, file_id: str, hh: models.SessionBase) -> Result:
        result = await views.get_folders_by_id(file_id, hh)
        return result

    @post('/create', summary="Create new folder or new file (新建文件夹)")
    async def create_folder(self, data: models.CatalogBase, hh: models.SessionBase) -> Result:
        result = await views.create_folder(data.id, hh)
        return result

    @post("/rename", summary="Rename folder or file (重命名文件夹)")
    async def rename_file(self, data: models.FilesBase, hh: models.SessionBase) -> Result:
        result = await views.rename_folder(data, hh)
        return result

    @post("/move", summary="Move folder (移动文件夹)")
    async def move_to_folder(self, data: models.CatalogMoveTo, hh: models.SessionBase) -> Result:
        result = await views.move_to_folder(data, hh)
        return result

    @get("/path/{folder_id: str}", summary="Get folder path (获取文件夹路径)")
    async def path_file(self, folder_id: str, hh: models.SessionBase) -> Result:
        result = await views.get_file_path(folder_id, hh)
        return result

    @post("/delete", summary="Delete file/folder (删除文件/文件夹)")
    async def delete_file(self, data: models.IsDelete, hh: models.SessionBase) -> Result:
        result = await views.delete_file(data, hh)
        return result
