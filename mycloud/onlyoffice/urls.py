#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import json
import os
import urllib.parse
from typing import Union
from litestar import Controller, get, post, put, Request
from litestar.response import Stream, Response
from litestar.di import Provide
from mycloud.onlyoffice import views
from mycloud.auth_middleware import auth, auth_url
from mycloud.models import SessionBase
from common.results import Result
from common.logging import logger
from common.messages import Msg


async def read_file(file_path, start_index=0):
    with open(file_path, 'rb') as f:
        f.seek(start_index)
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            yield chunk


class OnlyofficeController(Controller):
    path = "/onlyoffice"
    tags = ['OnlyOffice (办公套件)']
    dependencies = {"hh": Provide(auth), "hh_url": Provide(auth_url)}

    @get("/create", summary="create file（创建文件）")
    async def create(self, hh: SessionBase) -> Result:
        return Result(msg=Msg.OnlyOfficeCreateTips.get_text(hh.lang))

    @get("/edit/{file_id: str}", summary="edit file (编辑文件)")
    async def edit(self, file_id: str, request: Request, hh: SessionBase) -> Result:
        result = await views.edit(file_id, request, hh)
        return result

    @post("/track/{file_id: str}", summary="track file（保存文件）")
    async def save(self, file_id: str, request: Request, hh: SessionBase) -> Response:
        body = await request.body()
        result = await views.track(file_id, body.decode(encoding='utf-8'), hh)
        return Response(result, media_type='application/json', status_code=200)

    @post("/rename/{file_id: str}", summary="rename file（重命名文件）")
    async def rename(self, file_id: str, request: Request, hh: SessionBase) -> Response:
        body = await request.body()
        result = await views.rename(file_id, body.decode(encoding='utf-8'), hh)
        return Response(result, media_type='application/json', status_code=200)

    @post("/saveAs/{file_id: str}", summary="save as file（另存为文件）")
    async def save_as(self, file_id: str, request: Request, hh: SessionBase) -> Response:
        body = await request.body()
        result = await views.save_as(file_id, body.decode(encoding='utf-8'), hh)
        return Response(result, media_type='application/json', status_code=200)

    @post("/historyobj/{file_id: str}", summary="history file（历史文件）")
    async def history_obj(self, file_id: str, request: Request, hh: SessionBase) -> Response:
        body = await request.body()
        result = await views.history_obj(file_id, request, body.decode(encoding='utf-8'), hh)
        return Response(result, media_type='application/json', status_code=200)

    @get("/downloadhistory/{file_id: str}", summary="load history file（加载历史文件）")
    async def download_history(self, file_id: str, request: Request) -> Union[Stream, Response]:
        result = await views.download_history(file_id, request)
        if 'path' in result:
            file_name = urllib.parse.quote(os.path.basename(result['path']))
            headers = {'Accept-Ranges': 'bytes', 'Content-Length': str(os.path.getsize(result['path'])),
                       'Content-Disposition': f'attachment;filename="{file_name}"', 'Access-Control-Allow-Origin': '*'}
            return Stream(result['path'], 200, headers=headers, media_type='application/zip')
        else:
            return Response(json.dumps(result, ensure_ascii=False), media_type='application/json', status_code=200)

    @get("/download/{file_id: str}", summary="save as file（另存为文件）")
    async def download_from_path(self, file_id: str, hh: SessionBase) -> Union[Stream, Result]:
        try:
            folder_path = os.path.join('tmp', file_id)
            file_name = os.listdir(folder_path)[0]
            file_path = os.path.join(folder_path, file_name)
            headers = {'Accept-Ranges': 'bytes', 'Content-Length': str(os.path.getsize(file_path)),
                       'Content-Disposition': f'inline;filename="{urllib.parse.quote(file_name)}"'}
            logger.info(Msg.Download.get_text(hh.lang).format(file_path))
            return Stream(read_file(file_path), media_type='application/octet-stream', headers=headers)
        except:
            return Result(code=1, msg=Msg.DownloadError.get_text(hh.lang))

    @put("/restore/{file_id: str}", summary="restore from history file（从历史文件中恢复）")
    async def restore(self, file_id: str, request: Request, hh: SessionBase) -> Response:
        body = await request.body()
        result = await views.restore(file_id, body.decode(encoding='utf-8'), hh)
        return Response(result, media_type='application/json', status_code=200)
