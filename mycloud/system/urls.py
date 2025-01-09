#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

from fastapi import APIRouter, Depends
from mycloud import models
from mycloud.system import views
from mycloud.auth_middleware import auth


router = APIRouter(prefix='/system', tags=['system (系统)'], responses={404: {'description': 'Not found'}})


@router.get("/detail", summary="Get OS detail (获取操作系统信息)")
async def get_system_info(hh: models.SessionBase = Depends(auth)):
    result = await views.get_system_info(hh)
    return result


@router.get("/resource", summary="Get system resource (获取系统资源使用率)")
async def get_system_resource(hh: models.SessionBase = Depends(auth)):
    result = await views.get_resource(hh)
    return result


@router.get("/cpu", summary="Get CPU hardware detail (获取系统CPU硬件信息)")
async def get_cpu_detail(hh: models.SessionBase = Depends(auth)):
    result = await views.get_cpu_info(hh)
    return result


@router.get("/disk", summary="Get Disks detail (获取系统磁盘信息)")
async def get_disk_detail(hh: models.SessionBase = Depends(auth)):
    result = await views.get_disk_info(hh)
    return result


@router.get("/network", summary="Get Network Card detail (获取系统网卡信息)")
async def get_network_detail(hh: models.SessionBase = Depends(auth)):
    result = await views.get_net_info(hh)
    return result


@router.get("/clean/temporary/files", summary="Clear Temporary Files (清理临时文件)")
async def clean_temporary_file(hh: models.SessionBase = Depends(auth)):
    result = await views.remove_tmp_folder(hh)
    return result


@router.get("/version", summary="Get newest version (获取最新版本)")
async def get_version(hh: models.SessionBase = Depends(auth)):
    result = await views.get_new_version(hh)
    return result


@router.get("/update", summary="Update System (更新系统)")
async def update_system(hh: models.SessionBase = Depends(auth)):
    result = await views.update_system(hh)
    return result


@router.get("/resatrt", summary="Restart System (重启系统)")
async def restart_system(hh: models.SessionBase = Depends(auth)):
    result = await views.restart_system(hh)
    return result
