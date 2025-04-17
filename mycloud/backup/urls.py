#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

from litestar import Controller, get
from litestar.di import Provide
from mycloud import models
from mycloud.backup import views
from mycloud.auth_middleware import auth
from common.results import Result


class SyncController(Controller):
    path = "/syncing"
    tags = ['Backup (备份文件)']
    dependencies = {"hh": Provide(auth)}

    @get("/start", summary="Manual start backup (手动开始备份)")
    async def start_backup(self, hh: models.SessionBase) -> Result:
        result = await views.start_backup(hh)
        return result

    @get("/list", summary="Backup list (备份文件夹的列表)")
    async def index_backup(self, hh: models.SessionBase) -> Result:
        result = await views.index_backup(hh)
        return result

    @get("/set/{folder_id: str}/{is_backup: int}", summary="Add backup (设置目录要备份 / 取消备份)")
    async def add_backup(self, folder_id: str, is_backup: int, hh: models.SessionBase) -> Result:
        result = await views.add_backup(folder_id, is_backup, hh)
        return result
