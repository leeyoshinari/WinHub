#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import os
import traceback
import urllib.parse
from litestar import Controller, get, post, Request, WebSocket, websocket
from litestar.exceptions import WebSocketDisconnect
from litestar.response import Stream
from litestar.di import Provide
from mycloud import models
from mycloud.SSH import views
from mycloud.auth_middleware import auth
from common.results import Result
from common.logging import logger
from common.messages import Msg
from common.websocket import WebSSH


class ServerController(Controller):
    path = "/server"
    tags = ['SSH (连接服务器)']
    dependencies = {"hh": Provide(auth)}

    @post("/add", summary="Add server (添加服务器)")
    async def add_server(self, data: models.ServerModel, hh: models.SessionBase) -> Result:
        result = await views.save_server(data, hh)
        return result

    @get("/get", summary="Get server list (获取服务器列表)")
    async def get_server(self, hh: models.SessionBase) -> Result:
        result = await views.get_server(hh)
        return result

    @get("/delete/{server_id: str}", summary="Delete server (删除服务器)")
    async def delete_server(self, server_id: str, hh: models.SessionBase) -> Result:
        result = await views.delete_server(server_id, hh)
        return result

    @post("/file/upload", summary="Upload file (上传文件)")
    async def upload_file_to_ssh(self, request: Request, hh: models.SessionBase) -> Result:
        result = await views.upload_file_to_linux(request, hh)
        return result

    @get("/file/download", summary="Download file (下载文件)")
    async def download_file_from_ssh(self, server_id: str, file_path: str, hh: models.SessionBase) -> Stream:
        _, file_name = os.path.split(file_path)
        if not file_name:
            logger.error(f"{Msg.CommonLog.get_text(hh.lang).format(Msg.SSHExport.get_text(hh.lang), hh.username, hh.ip)}")
            return Result(code=1, msg=Msg.SSHExport.get_text(hh.lang))
        fp = await views.download_file_from_linux(server_id, file_path, hh)
        headers = {'Accept-Ranges': 'bytes', 'Content-Disposition': f'inline;filename="{urllib.parse.quote(file_name)}"'}
        return Stream(fp, media_type='application/octet-stream', headers=headers)

    @websocket('/open')
    async def shell_ssh(self, socket: WebSocket) -> None:
        await socket.accept()
        ws = WebSSH(socket)
        try:
            while True:
                data = await socket.receive_text()
                await ws.receive(data)
        except WebSocketDisconnect:
            logger.error("websocket disconnected.")
        except:
            logger.error(traceback.format_exc())
        finally:
            await ws.disconnect()
