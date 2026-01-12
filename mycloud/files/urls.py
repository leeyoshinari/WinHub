#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import os
import traceback
import urllib.parse
from typing import Union
from litestar import Controller, get, post, Request
from litestar.response import Stream, Response
from litestar.di import Provide
from mycloud import models
from mycloud.files import views
from mycloud.auth_middleware import auth, auth_url
from common.results import Result
from common.logging import logger
from common.messages import Msg
from settings import CONTENT_TYPE


async def read_file(file_path, start_index=0):
    with open(file_path, 'rb') as f:
        f.seek(start_index)
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            yield chunk


class FileController(Controller):
    path = "/file"
    tags = ['file (文件)']
    dependencies = {"hh": Provide(auth), "hh_url": Provide(auth_url)}

    @get("/get", summary="Query all files and folders in the current directory (查询当前目录下所有文件夹和文件)")
    async def query_files(self, file_id: str, q: str, sort_field: str, sort_type: str, hh: models.SessionBase, page: int = 1, page_size: int = 20) -> Result:
        query = models.SearchItems()
        query.q = q if q else ""
        query.sort_field = sort_field if sort_field else 'update_time'
        query.sort_type = sort_type if sort_type else 'desc'
        query.page = page
        query.page_size = page_size
        result = await views.get_all_files(file_id, query, hh)
        return result

    @post('/create', summary="Create new folder or new file (新建文件)")
    async def create_file(self, data: models.CatalogBase, hh: models.SessionBase) -> Result:
        result = await views.create_file(data.id, data.file_type, hh)
        return result

    @post("/rename", summary="Rename folder or file (重命名文件)")
    async def rename_file(self, data: models.FilesBase, hh: models.SessionBase) -> Result:
        result = await views.rename_file(data, hh)
        return result

    @get("/content/{file_id: str}", summary="Get content of a file (获取文本文件的内容)")
    async def get_file(self, file_id: str, hh: models.SessionBase) -> Result:
        result = await views.get_file_by_id(file_id, hh)
        return result

    @post("/save", summary="Save content to file (保存文本文件)")
    async def save_file(self, data: models.SaveFile, hh: models.SessionBase) -> Result:
        result = await views.save_txt_file(data, hh)
        return result

    @get("/copy/{file_id: str}", summary="Copy file (复制文件)")
    async def copy_file(self, file_id: str, hh: models.SessionBase) -> Result:
        result = await views.copy_file(file_id, hh)
        return result

    @get("/path/{file_id: str}", summary="Get file path (获取文件路径)")
    async def path_file(self, file_id: str, hh: models.SessionBase) -> Result:
        result = await views.get_file_path(file_id, hh)
        return result

    @get("/download/{file_id: str}", summary="Download file (下载文件)")
    async def download_file(self, file_id: str, hh: models.SessionBase) -> Union[Stream, Result]:
        try:
            result = await views.download_file(file_id, hh)
            headers = {'Accept-Ranges': 'bytes', 'Content-Length': str(os.path.getsize(result['path'])),
                       'Content-Disposition': f'inline;filename="{urllib.parse.quote(result["name"])}"',
                       'content-type': f'{CONTENT_TYPE.get(result["format"], "application/octet-stream")}'}
            return Stream(read_file(result['path']), media_type=CONTENT_TYPE.get(result["format"], 'application/octet-stream'), headers=headers)
        except:
            logger.error(traceback.format_exc())
            return Result(code=1, msg=Msg.DownloadError.get_text(hh.lang))

    @get("/onlyoffice/{file_id: str}", summary="Download office file (下载 onlyoffice 文件)")
    async def onlyoffice_file(self, file_id: str, hh_url: models.SessionBase) -> Union[Stream, Result]:
        try:
            result = await views.download_file(file_id, hh_url)
            headers = {'Accept-Ranges': 'bytes', 'Content-Length': str(os.path.getsize(result['path'])),
                       'Content-Disposition': f'inline;filename="{urllib.parse.quote(result["name"])}"',
                       'content-type': f'{CONTENT_TYPE.get(result["format"], "application/octet-stream")}'}
            return Stream(read_file(result['path']), media_type=CONTENT_TYPE.get(result["format"], 'application/octet-stream'), headers=headers)
        except:
            logger.error(traceback.format_exc())
            return Result(code=1, msg=Msg.DownloadError.get_text(hh_url.lang))

    @post("/export", summary="Export multiple files (导出多个文件, 或单个文件夹下的所有文件)")
    async def zip_file(self, data: models.DownloadFile, hh: models.SessionBase) -> Result:
        try:
            if len(data.ids) == 0:
                return Result(code=1, msg=Msg.ExportError1.get_text(hh.lang))
            if data.file_type == 'folder' and len(data.ids) > 1:
                return Result(code=1, msg=Msg.ExportError2.get_text(hh.lang))
            return await views.zip_file(data, hh)
        except:
            logger.error(traceback.format_exc())
            return Result(code=1, msg=Msg.ExportError3.get_text(hh.lang))

    @post("/move", summary="Move file (移动文件)")
    async def move_to_folder(self, data: models.CatalogMoveTo, hh: models.SessionBase) -> Result:
        result = await views.move_to_folder(data, hh)
        return result

    @post("/import", summary="Import files from local file in server (服务器本地文件直接导入)")
    async def import_file(self, data: models.ImportLocalFileByPath, hh: models.SessionBase) -> Result:
        result = await views.upload_file_by_path(data, hh)
        return result

    @post("/upload", summary="Upload files (上传文件)")
    async def upload_file(self, request: Request, hh: models.SessionBase) -> Result:
        result = await views.upload_file(request, hh)
        return result

    @post("/uploadImage", summary="Upload background image (上传背景图片)")
    async def upload_image(self, request: Request, hh: models.SessionBase) -> Result:
        result = await views.upload_image(request, hh)
        return result

    @post("/share", summary="Share file (分享文件)")
    async def share_file(self, data: models.ShareFile, hh: models.SessionBase) -> Result:
        result = await views.share_file(data, hh)
        return result

    @get("/save/{share_id: int}/{folder_id: str}", summary="Save shared file (保存分享的文件至网盘)")
    async def save_share(self, share_id: int, folder_id: str, hh: models.SessionBase) -> Result:
        result = await views.save_shared_to_myself(share_id, folder_id, hh)
        return result

    @get("/playVideo/{file_id: str}", summary="Play video (播放视频)")
    async def play_video(self, file_id: str, request: Request, hh: models.SessionBase) -> Union[Stream, Result]:
        try:
            result = await views.download_file(file_id, hh)
            header_range = request.headers.get('range', '0-')
            start_index = int(header_range.strip('bytes=').split('-')[0])
            file_size = os.path.getsize(result['path'])
            content_range = f"bytes {start_index}-{file_size - 1}/{file_size}"
            headers = {'Accept-Ranges': 'bytes', 'Content-Length': str(file_size - start_index),
                       'Content-Range': content_range, 'Content-Disposition': f'inline;filename="{urllib.parse.quote(result["name"])}"',
                       'content-type': f'{CONTENT_TYPE.get(result["format"], "application/octet-stream")}'}
            return Stream(read_file(result['path'], start_index=start_index), media_type=CONTENT_TYPE.get(result["format"], 'application/octet-stream'), headers=headers, status_code=206)
        except:
            logger.error(traceback.format_exc())
            return Result(code=1, msg=Msg.VideoError.get_text(hh.lang))

    @get("/export/xmind/{file_id: str}", summary="Export xmind file (导出 xmind 文件)")
    async def export_file(self, file_id: str, hh: models.SessionBase) -> Union[Stream, Result]:
        try:
            result = await views.export_xmind_file(file_id, hh)
            headers = {'Accept-Ranges': 'bytes', 'Content-Length': str(os.path.getsize(result['path'])),
                       'Content-Disposition': f'inline;filename="{urllib.parse.quote(result["name"])}"',
                       'content-type': f'{CONTENT_TYPE.get(result["format"], "application/octet-stream")}'}
            return Stream(read_file(result['path']), media_type=CONTENT_TYPE.get(result["format"], 'application/octet-stream'), headers=headers)
        except:
            logger.error(traceback.format_exc())
            return Result(code=1, msg=Msg.DownloadError.get_text(hh.lang))

    @get("/export/md/{file_id: str}", summary="Export markdown to html (导出 markdown 转 html)")
    async def md2html(self, file_id: str, hh: models.SessionBase) -> Union[Response, Result]:
        try:
            result = await views.markdown_to_html(file_id, hh)
            headers = {'Accept-Ranges': 'bytes', 'Content-Disposition': f'inline;filename="{urllib.parse.quote(result["name"])}"'}
            return Response(result['data'].encode('utf-8'), media_type=CONTENT_TYPE.get(result["format"], 'application/octet-stream'), headers=headers)
        except:
            logger.error(traceback.format_exc())
            return Result(code=1, msg=Msg.Failure.get_text(hh.lang))

    @get("/shortcuts", summary="Get all shortcuts (查询快捷方式数据)")
    async def get_shortcuts(self, hh: models.SessionBase) -> Result:
        result = await views.get_shortcuts(hh)
        return result

    @get("/shortcuts/save/{file_id: str}", summary="Save file to shortcuts (把文件添加到桌面快捷方式)")
    async def set_shortcuts(self, file_id: str, hh: models.SessionBase) -> Result:
        result = await views.set_shortcuts(file_id, hh)
        return result

    @get("/shortcuts/delete/{file_id: int}", summary="Delete shortcuts (删除桌面快捷方式)")
    async def delete_shortcuts(self, file_id: int, hh: models.SessionBase) -> Result:
        result = await views.delete_shortcuts(file_id, hh)
        return result
