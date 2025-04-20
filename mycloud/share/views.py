#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import traceback
from sqlalchemy import desc
from mycloud import models
from mycloud.database import Shares
from common.results import Result
from common.messages import Msg
from common.logging import logger


async def open_share_file(share_id: int, hh: models.SessionBase) -> dict:
    try:
        share = Shares.get(share_id)
        if share.total_times == 0 or share.times < share.total_times:
            Shares.update(share, times=share.times + 1)
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
        files = Shares.query(username=hh.groupname).order_by(desc(Shares.id)).all()
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
        share = Shares.filter(Shares.id.in_(query.ids)).all()
        for s in share:
            Shares.delete(s)
        result.msg = f"{Msg.Delete.get_text(hh.lang).format('')}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(Msg.Delete.get_text(hh.lang).format(query.ids) + Msg.Success.get_text(hh.lang), query.ids, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Delete.get_text(hh.lang).format('')}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result
