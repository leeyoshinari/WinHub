#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari
import os
import traceback
from sqlalchemy import desc
from mycloud.database import Servers
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
        datas = get_server_info(host=query.host, port=int(query.port), user=query.user, pwd=query.pwd, current_time=query.t)
        if datas['code'] == 0:
            Servers.create(id=query.t, host=query.host, port=query.port, user=query.user, username=hh.groupname, pwd=query.pwd, system=datas['system'], cpu=datas['cpu'], mem=datas['mem'], disk=datas['disk'])
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
        server = Servers.get_one(server_id)
        Servers.delete(server)
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
        server = Servers.query(username=hh.groupname).order_by(desc(Servers.id)).all()
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
        server = Servers.get_one(server_id)
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
        server = Servers.get_one(server_id)
        upload_obj = UploadAndDownloadFile(server)
        fp = upload_obj.download(file_path)
        logger.info(Msg.CommonLog.get_text(hh.lang).format(Msg.Download.get_text(hh.lang).format(file_path), hh.username, hh.ip))
        return fp
    except:
        logger.error(traceback.format_exc())
        return None
