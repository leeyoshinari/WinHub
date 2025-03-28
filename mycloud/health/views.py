#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import traceback
from mycloud import models
from common.results import Result
from common.messages import Msg
from common.logging import logger


async def get_all_data(start_type: int, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        datas = await models.Health.filter(mode=start_type, username=hh.username).order_by('id')
        result.data = datas
        result.msg = f'{Msg.SystemInfo.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}'
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f'{Msg.SystemInfo.get_text(hh.lang)} {Msg.Failure.get_text(hh.lang)}'
    return result


async def set_data(query: models.HealthData, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        if query.healthType == 3:
            if query.value1:
                if query.value > query.value1:
                    _ = await models.Health.create(mode=333, value=query.value1, username=hh.username)
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
        _ = await models.Health.create(mode=query.healthType, value=query.value, username=hh.username)
        result.msg = f'{Msg.HealthSetData.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}'
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f'{Msg.HealthSetData.get_text(hh.lang)} {Msg.Failure.get_text(hh.lang)}'
    return result
