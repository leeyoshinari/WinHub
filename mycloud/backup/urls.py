#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

from fastapi import APIRouter, Depends
from mycloud import models
from mycloud.backup import views
from mycloud.auth_middleware import auth


router = APIRouter(prefix='/syncing', tags=['Backup (备份文件)'], responses={404: {'description': 'Not found'}})


@router.get("/start", summary="Manual start backup (手动开始备份)")
async def start_backup(hh: models.SessionBase = Depends(auth)):
    result = await views.start_backup(hh)
    return result


@router.get("/list", summary="Backup list (备份文件夹的列表)")
async def index_backup(hh: models.SessionBase = Depends(auth)):
    result = await views.index_backup(hh)
    return result


@router.get("/set/{folder_id}/{is_backup}", summary="Add backup (设置目录要备份 / 取消备份)")
async def add_backup(folder_id: str, is_backup: int, hh: models.SessionBase = Depends(auth)):
    result = await views.add_backup(folder_id, is_backup, hh)
    return result
