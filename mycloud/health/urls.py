#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

from fastapi import APIRouter, Depends
from mycloud import models
from mycloud.health import views
from mycloud.auth_middleware import auth


router = APIRouter(prefix='/health', tags=['health (健康)'], responses={404: {'description': 'Not found'}})


@router.get("/getData/{health_type}", summary="Get all datas (获取所有数据，用于可视化)")
async def get_all_data(start_type: int, hh: models.SessionBase = Depends(auth)):
    result = await views.get_all_data(start_type, hh)
    return result


@router.post("/set", summary="Set health data (设置数据)")
async def set_health_data(query: models.HealthData, hh: models.SessionBase = Depends(auth)):
    result = await views.set_data(query, hh)
    return result
