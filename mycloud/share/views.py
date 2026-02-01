#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import traceback
from mycloud import models
from mycloud.database import Shares
from common.results import Result
from common.messages import Msg
from common.logging import logger


async def open_share_file(share_id: int, hh: models.SessionBase) -> dict:
    try:
        share = await Shares.get(share_id)
        if share.total_times == 0 or share.times < share.total_times:
            await Shares.update(share.id, times=share.times + 1)
            result = {'type': 0, 'path': share.path, 'name': share.name, 'format': share.format, 'file_id': share.file_id}
            logger.info(f"{share.name} - {Msg.ShareOpen.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}, Id: {share.id}, IP: {hh.ip}")
        else:
            logger.warning(f"{share.name} - {Msg.ShareTimes.get_text(hh.lang)}, Id: {share.id}, IP: {hh.ip}")
            result = {'type': 404}
    except:
        logger.error(traceback.format_exc())
        result = {'type': 404}
    return result


async def get_share_file(hh: models.SessionBase) -> Result:
    result = Result()
    try:
        files = await Shares.query().equal(username=hh.groupname).order_by(Shares.id.desc()).all()
        result.data = [models.ShareFileList.from_orm_format(f).model_dump() for f in files]
        result.total = len(result.data)
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def delete_file(query: models.IsDelete, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        share = await Shares.query().isin(id=query.ids).all()
        for s in share:
            await Shares.query().equal(id=s.id).delete()
        result.msg = f"{Msg.Delete.get_text(hh.lang).format('')}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(Msg.Delete.get_text(hh.lang).format(query.ids) + Msg.Success.get_text(hh.lang), query.ids, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Delete.get_text(hh.lang).format('')}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result
