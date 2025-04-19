#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import traceback
from sqlalchemy import asc, desc
from mycloud import models
from mycloud.database import Health
from common.results import Result
from common.messages import Msg
from common.logging import logger


async def get_all_data(health_type: int, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        x = []
        y1 = []
        datas = Health.query(mode=health_type, username=hh.username).with_entities(Health.create_time, Health.value).order_by(asc(Health.create_time)).all()
        if health_type == 1:    # 体重 + BMI
            height_obj = Health.query(mode=0, username=hh.username).order_by(desc(Health.id)).first()
            y2 = []
            for d in datas:
                x.append(d[0].strftime("%Y-%m-%d"))
                y1.append(d[1] / (height_obj.value / 100)**2)
                y2.append(d[1])
            result.data = {'x': x, 'y1': y1, 'y2': y2}

        elif health_type == 3:  # 血压和心跳
            y3_data = Health.query(mode=2, username=hh.username).with_entities(Health.create_time, Health.value).order_by(asc(Health.create_time)).all()
            y2_data = Health.query(mode=333, username=hh.username).with_entities(Health.create_time, Health.value).order_by(asc(Health.create_time)).all()
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
        if query.healthType == 3:
            if query.value1:
                if query.value > query.value1:
                    _ = Health.create(mode=333, value=query.value1, username=hh.username)
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
        _ = Health.create(mode=query.healthType, value=query.value, username=hh.username)
        result.msg = f'{Msg.HealthSetData.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}'
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f'{Msg.HealthSetData.get_text(hh.lang)} {Msg.Failure.get_text(hh.lang)}'
    return result
