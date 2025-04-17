#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

from litestar import Controller, get
from litestar.di import Provide
from mycloud import models
from mycloud.system import views
from mycloud.auth_middleware import auth
from common.results import Result


class SystemController(Controller):
    path = "/system"
    tags = ['system (系统)']
    dependencies = {"hh": Provide(auth)}

    @get("/detail", summary="Get OS detail (获取操作系统信息)")
    async def get_system_info(self, hh: models.SessionBase) -> Result:
        result = await views.get_system_info(hh)
        return result

    @get("/resource", summary="Get system resource (获取系统资源使用率)")
    async def get_system_resource(self, hh: models.SessionBase) -> Result:
        result = await views.get_resource(hh)
        return result

    @get("/cpu", summary="Get CPU hardware detail (获取系统CPU硬件信息)")
    async def get_cpu_detail(self, hh: models.SessionBase) -> Result:
        result = await views.get_cpu_info(hh)
        return result

    @get("/disk", summary="Get Disks detail (获取系统磁盘信息)")
    async def get_disk_detail(self, hh: models.SessionBase) -> Result:
        result = await views.get_disk_info(hh)
        return result

    @get("/network", summary="Get Network Card detail (获取系统网卡信息)")
    async def get_network_detail(self, hh: models.SessionBase) -> Result:
        result = await views.get_net_info(hh)
        return result

    @get("/clean/temporary/files", summary="Clear Temporary Files (清理临时文件)")
    async def clean_temporary_file(self, hh: models.SessionBase) -> Result:
        result = await views.remove_tmp_folder(hh)
        return result

    @get("/update/status", summary="Get update status (获取更新状态)")
    async def get_update_status(self, hh: models.SessionBase) -> Result:
        return Result(code=0, data=views.get_update_status(hh))

    @get("/version", summary="Get newest version (获取最新版本)")
    async def get_version(self, hh: models.SessionBase) -> Result:
        result = await views.get_new_version(hh)
        return result

    @get("/update/log", summary="Get newest version (获取最新日志)")
    async def get_version_log(self, hh: models.SessionBase) -> Result:
        result = await views.get_version_log(hh)
        return result

    @get("/update", summary="Update System (更新系统)")
    async def update_system(self, hh: models.SessionBase) -> Result:
        result = await views.update_system(hh)
        return result

    @get("/resatrt/{start_type: int}", summary="Restart System (重启系统)")
    async def restart_system(self, start_type: int, hh: models.SessionBase) -> Result:
        result = await views.restart_system(start_type, hh)
        return result
