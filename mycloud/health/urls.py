#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

from litestar import Controller, get, post
from litestar.di import Provide
from mycloud import models
from mycloud.health import views
from mycloud.auth_middleware import auth
from common.results import Result


class HealthController(Controller):
    path = "/health"
    tags = ['health (健康)']
    dependencies = {"hh": Provide(auth)}

    @get("/get/{health_type: int}", summary="Get all datas (获取所有数据，用于可视化)")
    async def get_all_data(self, health_type: int, hh: models.SessionBase) -> Result:
        result = await views.get_all_data(health_type, hh)
        return result

    @post("/set", summary="Set health data (设置数据)")
    async def set_health_data(self, data: models.HealthData, hh: models.SessionBase) -> Result:
        result = await views.set_data(data, hh)
        return result
