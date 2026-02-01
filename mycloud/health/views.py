#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import traceback
from mycloud import models
from mycloud.database import Health
from common.results import Result
from common.messages import Msg
from common.logging import logger


async def get_all_data(health_type: int, username: str, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        x = []
        y1 = []
        datas = await Health.query().select('create_time', 'value').equal(mode=health_type, username=username).order_by(Health.create_time.asc()).all()
        if health_type == 1:    # 体重 + BMI
            height_obj = await Health.query().equal(mode=0, username=username).order_by(Health.id.desc()).first()
            y2 = []
            for d in datas:
                x.append(d[0].strftime("%Y-%m-%d"))
                y1.append(d[1] / (height_obj.value / 100)**2)
                y2.append(d[1])
            result.data = {'x': x, 'y1': y1, 'y2': y2}

        elif health_type == 3:  # 血压和心跳
            y3_data = await Health.query().select('create_time', 'value').equal(mode=2, username=username).order_by(Health.create_time.asc()).all()
            y2_data = await Health.query().select('create_time', 'value').equal(mode=333, username=username).order_by(Health.create_time.asc()).all()
            y2 = []
            y3 = []
            for i in range(len(datas)):
                x.append(datas[i][0].strftime("%Y-%m-%d"))
                y1.append(datas[i][1])
                y2.append(y2_data[i][1])
                y3.append(y3_data[i][1])
            result.data = {'x': x, 'y1': y1, 'y2': y2, 'y3': y3}

        else:
            for d in datas:
                x.append(d[0].strftime("%Y-%m-%d"))
                y1.append(d[1])
            result.data = {'x': x, 'y1': y1}
        if len(result.data['x']) > 1:
            result.msg = f'{Msg.Query.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}'
        else:
            result.msg = Msg.HealthBlank.get_text(hh.lang)
            result.code = 1
            result.data = None
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f'{Msg.Query.get_text(hh.lang)} {Msg.Failure.get_text(hh.lang)}'
    return result


async def set_data(query: models.HealthData, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        if query.healthType == 3:   # 血压数据
            if query.value1:
                if query.value > query.value1:  # 高压大于低压
                    await Health.create(mode=333, value=query.value1, username=query.username)  # 低压
                else:
                    result.msg = Msg.HealthBloodPressureErr.get_text(hh.lang)
                    result.code = 1
                    logger.error(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
                    return result
            else:
                result.msg = Msg.HealthNoData.get_text(hh.lang)
                result.code = 1
                logger.error(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
                return result
        await Health.create(mode=query.healthType, value=query.value, username=query.username)
        result.msg = f'{Msg.HealthSetData.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}'
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f'{Msg.HealthSetData.get_text(hh.lang)} {Msg.Failure.get_text(hh.lang)}'
    return result
