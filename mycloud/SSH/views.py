#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari
import os
import traceback
from tortoise import transactions
from mycloud import models
from common.results import Result
from common.messages import Msg
from common.logging import logger
from common.ssh import UploadAndDownloadFile, get_server_info


if not os.path.exists('tmp'):
    os.mkdir('tmp')


async def save_server(query: models.ServerModel, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        async with transactions.in_transaction():
            datas = get_server_info(host=query.host, port=int(query.port), user=query.user, pwd=query.pwd, current_time=query.t)
            if datas['code'] == 0:
                _ = await models.Servers.create(id=query.t, host=query.host, port=query.port, user=query.user, creator=hh.username,
                        pwd=query.pwd, system=datas['system'], cpu=datas['cpu'], mem=datas['mem'], disk=datas['disk'])
            else:
                result.code = 1
                result.msg = datas['msg']
                return result
        result.msg = f"{Msg.Save.get_text(hh.lang).format(query.host)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Save.get_text(hh.lang).format(query.host)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def delete_server(server_id: str, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        server = await models.Servers.get(id=server_id)
        await server.delete()
        await server.save()
        result.msg = f"{Msg.Delete.get_text(hh.lang).format(server.host)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Delete.get_text(hh.lang).format(server_id)}{Msg.Success.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def get_server(hh: models.SessionBase) -> Result:
    result = Result()
    try:
        async with transactions.in_transaction():
            server = await models.Servers.filter(creator=hh.username)
            server_list = [models.ServerListModel.model_validate(f).model_dump() for f in server]
        result.data = server_list
        result.total = len(server_list)
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def upload_file_to_linux(query, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        query = await query.form()
        server_id = query['id']
        file_name = query['file'].filename
        remote_path = query['remotePath']
        temp_path = os.path.join('tmp', file_name)
        with open(temp_path, 'wb') as f:
            f.write(query['file'].file.read())
        remote_path = remote_path if remote_path else '/home'
        server = await models.Servers.get(id=server_id)
        upload_obj = UploadAndDownloadFile(server)
        _ = upload_obj.upload(temp_path, f'{remote_path}/{file_name}')
        os.remove(temp_path)
        del upload_obj
        result.msg = f"{Msg.Upload.get_text(hh.lang).format(file_name)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Upload.get_text(hh.lang).format(file_name)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def download_file_from_linux(server_id, file_path, hh: models.SessionBase):
    try:
        server = await models.Servers.get(id=server_id)
        upload_obj = UploadAndDownloadFile(server)
        fp = upload_obj.download(file_path)
        del upload_obj
        logger.info(Msg.CommonLog.get_text(hh.lang).format(Msg.Download.get_text(hh.lang).format(file_path), hh.username, hh.ip))
        return fp
    except:
        del upload_obj
        logger.error(traceback.format_exc())
        return None
