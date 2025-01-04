#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

from fastapi import APIRouter, Depends
from mycloud import models
from mycloud.folders import views
from mycloud.auth_middleware import auth


router = APIRouter(prefix='/folder', tags=['folder (文件夹)'], responses={404: {'description': 'Not found'}})


@router.get("/getDisk", summary="Get disk usage (获取磁盘空间使用数据)")
async def get_disk_info(hh: models.SessionBase = Depends(auth)):
    result = await views.get_disk_usage(hh)
    return result


@router.get('/get/{file_id}', summary="Query all folders in the current directory (查询当前目录下所有的文件夹)")
async def get_folder_name(file_id: str, hh: models.SessionBase = Depends(auth)):
    result = await views.get_folders_by_id(file_id, hh)
    return result


@router.post('/create', summary="Create new folder or new file (新建文件夹)")
async def create_folder(query: models.CatalogBase, hh: models.SessionBase = Depends(auth)):
    result = await views.create_folder(query.id, hh)
    return result


@router.post("/rename", summary="Rename folder or file (重命名文件夹)")
async def rename_file(query: models.FilesBase, hh: models.SessionBase = Depends(auth)):
    result = await views.rename_folder(query, hh)
    return result


@router.post("/move", summary="Move folder (移动文件夹)")
async def move_to_folder(query: models.CatalogMoveTo, hh: models.SessionBase = Depends(auth)):
    result = await views.move_to_folder(query, hh)
    return result


@router.get("/path/{folder_id}", summary="Get folder path (获取文件夹路径)")
async def path_file(folder_id: str, hh: models.SessionBase = Depends(auth)):
    result = await views.get_file_path(folder_id, hh)
    return result


@router.post("/delete", summary="Delete file/folder (删除文件/文件夹)")
async def delete_file(query: models.IsDelete, hh: models.SessionBase = Depends(auth)):
    result = await views.delete_file(query, hh)
    return result
