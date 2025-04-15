#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import os
import traceback
import urllib.parse
from typing import Union
from litestar import Controller, get, post, Request, Response
from litestar.response import Stream
from litestar.di import Provide
from mycloud import models
from mycloud.share import views
from mycloud.auth_middleware import auth
from common.results import Result
from common.logging import logger
from common.xmind import read_xmind, generate_xmind8
from common.sheet import read_sheet
from settings import CONTENT_TYPE, HTML404


async def read_file(file_path, start_index=0):
    with open(file_path, 'rb') as f:
        f.seek(start_index)
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            yield chunk


class ShareController(Controller):
    path = "/share"
    tags = ['share (文件分享)']
    dependencies = {"hh": Provide(auth)}

    @get("/list", summary="Share file list (分享文件列表)")
    async def get_share_list(self, hh: models.SessionBase) -> Result:
        result = await views.get_share_file(hh)
        return result

    @get("/get/{file_id: int}", summary="Open share link (打开文件分享链接)")
    async def get_share_file(self, file_id: int, request: Request) -> Union[Stream, Response]:
        try:
            hh = models.SessionBase(ip=request.headers.get('x-real-ip', ''), lang=request.headers.get('lang', 'en'), username='')
            result = await views.open_share_file(file_id, hh)
            if result['type'] == 0:
                if result["format"] in ['md', 'docu', 'py']:
                    res = Result()
                    with open(result['path'], 'r', encoding='utf-8') as f:
                        res.data = f.read()
                    res.msg = result['name']
                    return res
                if result["format"] == 'xmind':
                    res = Result()
                    xmind = read_xmind(result['path'])
                    res.data = xmind
                    res.msg = result['name']
                    return res
                if result["format"] == 'sheet':
                    res = Result()
                    sheet = read_sheet(result['path'])
                    res.data = sheet
                    res.msg = result['name']
                    return res
                else:
                    if os.path.exists(result['path']):
                        headers = {'Content-Disposition': f'inline;filename="{urllib.parse.quote(result["name"])}"', 'Cache-Control': 'no-store'}
                        return Stream(read_file(result['path']), media_type=CONTENT_TYPE.get(result["format"], 'application/octet-stream'), headers=headers)
                    else:
                        return Response(status_code=404, content=HTML404, media_type="text/html")
            else:
                return Response(status_code=404, content=HTML404, media_type="text/html")
        except:
            logger.error(traceback.format_exc())
            return Response(status_code=404, content=HTML404, media_type="text/html")

    @get("/export/{file_id: int}", summary="Export file (导出文件)")
    async def export_share_file(self, file_id: int, request: Request) -> Union[Stream, Response]:
        try:
            hh = models.SessionBase(ip=request.headers.get('x-real-ip', ''), lang=request.headers.get('lang', 'en'), username='')
            result = await views.open_share_file(file_id, hh)
            if result['type'] == 0:
                if result["format"] == 'xmind':
                    file_path = generate_xmind8(result['file_id'], result['name'], result['path'])
                    result['path'] = file_path
                headers = {'Accept-Ranges': 'bytes', 'Content-Length': str(os.path.getsize(result['path'])),
                           'Content-Disposition': f'inline;filename="{urllib.parse.quote(result["name"])}"'}
                return Stream(read_file(result['path']), media_type=CONTENT_TYPE.get(result["format"], 'application/octet-stream'), headers=headers)
            else:
                return Response(status_code=404, content=HTML404, media_type="text/html")
        except:
            logger.error(traceback.format_exc())
            return Response(status_code=404, content=HTML404, media_type="text/html")

    @post("/delete", summary="Delete share (删除文件分享)")
    async def delete_file(self, data: models.IsDelete, hh: models.SessionBase) -> Result:
        result = await views.delete_file(data, hh)
        return result
