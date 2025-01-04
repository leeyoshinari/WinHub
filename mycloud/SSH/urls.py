#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import os
import traceback
from fastapi import APIRouter, Request, Depends, WebSocket, WebSocketDisconnect
from mycloud import models
from mycloud.SSH import views
from mycloud.auth_middleware import auth
from mycloud.responses import StreamResponse
from common.results import Result
from common.logging import logger
from common.messages import Msg
from common.websocket import WebSSH


router = APIRouter(prefix='/server', tags=['SSH (连接服务器)'], responses={404: {'description': 'Not found'}})


@router.post("/add", summary="Add server (添加服务器)")
async def add_server(query: models.ServerModel, hh: models.SessionBase = Depends(auth)):
    result = await views.save_server(query, hh)
    return result


@router.get("/get", summary="Get server list (获取服务器列表)")
async def get_server(hh: models.SessionBase = Depends(auth)):
    result = await views.get_server(hh)
    return result


@router.get("/delete/{server_id}", summary="Delete server (删除服务器)")
async def delete_server(server_id: str, hh: models.SessionBase = Depends(auth)):
    result = await views.delete_server(server_id, hh)
    return result


@router.post("/file/upload", summary="Upload file (上传文件)")
async def upload_file_to_ssh(query: Request, hh: models.SessionBase = Depends(auth)):
    result = await views.upload_file_to_linux(query, hh)
    return result


@router.get("/file/download", summary="Download file (下载文件)")
async def download_file_from_ssh(server_id: str, file_path: str, hh: models.SessionBase = Depends(auth)):
    _, file_name = os.path.split(file_path)
    if not file_name:
        logger.error(f"{Msg.CommonLog[hh['lang']].format(Msg.SSHExport.get_text(hh.lang), hh.username, hh.ip)}")
        return Result(code=1, msg=Msg.SSHExport.get_text(hh.lang))
    fp = await views.download_file_from_linux(server_id, file_path, hh)
    headers = {'Accept-Ranges': 'bytes', 'Content-Disposition': f'inline;filename="{file_name}"'}
    return StreamResponse(fp, media_type='application/octet-stream', headers=headers)


@router.websocket('/open')
async def shell_ssh(websocket: WebSocket):
    await websocket.accept()
    ws = WebSSH(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await ws.receive(data)
    except WebSocketDisconnect:
        logger.error("websocket disconnected.")
    except:
        logger.error(traceback.format_exc())
    finally:
        await ws.disconnect()
