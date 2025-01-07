#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import json
import os
from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse
from mycloud.onlyoffice import views
from mycloud.responses import StreamResponse, MyResponse
from mycloud.auth_middleware import auth, auth_url
from mycloud.models import SessionBase
from common.results import Result
from common.logging import logger
from common.messages import Msg


router = APIRouter(prefix='/onlyoffice', tags=['OnlyOffice (办公套件)'], responses={404: {'description': 'Not found'}})


async def read_file(file_path, start_index=0):
    with open(file_path, 'rb') as f:
        f.seek(start_index)
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            yield chunk


@router.get("/create", summary="create file（创建文件）")
async def create(hh: SessionBase = Depends(auth)):
    return Result(msg=Msg.OnlyOfficeCreateTips.get_text(hh.lang))


@router.get("/edit/{file_id}", summary="edit file (编辑文件)")
async def edit(file_id: str, request: Request, hh: SessionBase = Depends(auth)):
    result = await views.edit(file_id, request, hh)
    return result


@router.post("/track/{file_id}", summary="track file（保存文件）")
async def save(file_id: str, request: Request, hh: SessionBase = Depends(auth_url)):
    body = await request.body()
    result = await views.track(file_id, body.decode(encoding='utf-8'), hh)
    return MyResponse(result, media_type='application/json', status_code=200)


@router.post("/rename/{file_id}", summary="rename file（重命名文件）")
async def rename(file_id: str, request: Request, hh: SessionBase = Depends(auth)):
    body = await request.body()
    result = await views.rename(file_id, body.decode(encoding='utf-8'), hh)
    return MyResponse(result, media_type='application/json', status_code=200)


@router.post("/saveAs/{file_id}", summary="save as file（另存为文件）")
async def save_as(file_id: str, request: Request, hh: SessionBase = Depends(auth)):
    body = await request.body()
    result = await views.save_as(file_id, body.decode(encoding='utf-8'), hh)
    return MyResponse(result, media_type='application/json', status_code=200)


@router.post("/historyobj/{file_id}", summary="history file（历史文件）")
async def history_obj(file_id: str, request: Request, hh: SessionBase = Depends(auth)):
    body = await request.body()
    result = await views.history_obj(file_id, request, body.decode(encoding='utf-8'), hh)
    return MyResponse(result, media_type='application/json', status_code=200)


@router.get("/downloadhistory/{file_id}", summary="load history file（加载历史文件）")
async def download_history(file_id: str, request: Request):
    result = await views.download_history(file_id, request)
    if 'path' in result:
        file_name = os.path.basename(result['path'])
        headers = {'Accept-Ranges': 'bytes', 'Content-Length': str(os.path.getsize(result['path'])),
                   'Content-Disposition': f'attachment;filename="{file_name}"', 'Access-Control-Allow-Origin': '*'}
        return FileResponse(result['path'], 200, headers=headers, media_type='application/zip')
    else:
        return MyResponse(json.dumps(result, ensure_ascii=False), media_type='application/json', status_code=200)


@router.get("/download/{file_id}", summary="save as file（另存为文件）")
async def download_from_path(file_id: str, hh: SessionBase = Depends(auth)):
    try:
        folder_path = os.path.join('tmp', file_id)
        file_name = os.listdir(folder_path)[0]
        file_path = os.path.join(folder_path, file_name)
        headers = {'Accept-Ranges': 'bytes', 'Content-Length': str(os.path.getsize(file_path)),
                   'Content-Disposition': f'inline;filename="{file_name}"'}
        logger.info(Msg.Download.get_text(hh.lang).format(file_path))
        return StreamResponse(read_file(file_path), media_type='application/octet-stream', headers=headers)
    except:
        return Result(code=1, msg=Msg.DownloadError.get_text(hh.lang))


@router.put("/restore/{file_id}", summary="restore from history file（从历史文件中恢复）")
async def restore(file_id: str, request: Request, hh: SessionBase = Depends(auth)):
    body = await request.body()
    result = await views.restore(file_id, body.decode(encoding='utf-8'), hh)
    return MyResponse(result, media_type='application/json', status_code=200)
