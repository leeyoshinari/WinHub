#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import os
import json
import asyncio
import traceback
import urllib.parse
from typing import Any, Union, AsyncGenerator
from litestar import Controller, get, post, Request
from litestar.response import Stream, ServerSentEvent
from litestar.di import Provide
from settings import KARAOKE_PATH, CONTENT_TYPE, KTV_TMP_PATH
from mycloud import models
from mycloud.auth_middleware import auth, no_auth
from mycloud.karaoke import views
from common.messages import Msg
from common.results import Result
from common.logging import logger


async def read_file(file_path, start_index=0):
    with open(file_path, 'rb') as f:
        f.seek(start_index)
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            yield chunk


# views.init_history()


class KaraokeController(Controller):
    path = "/karaoke"
    tags = ['karaoke (卡拉OK)']
    dependencies = {"hh": Provide(auth), "no_hh": Provide(no_auth)}

    @post('/upload', summary="上传歌曲")
    async def upload_file(self, data: Request, hh: models.SessionBase) -> Result:
        result = await views.upload_file(data, hh)
        return result

    @get("/list", summary="歌曲列表")
    async def song_list(self, no_hh: models.SessionBase, q: str = "", page: int = 0) -> Result:
        result = await views.get_list(q, page, no_hh)
        return result

    @get("/delete/{file_id: int}", summary="删除歌曲")
    async def delete_song(self, file_id: int, hh: models.SessionBase) -> Result:
        result = await views.delete_song(file_id, hh)
        return result

    @get("/deleteHistory/{file_id: int}", summary="删除点歌历史记录")
    async def delete_history(self, file_id: int, no_hh: models.SessionBase) -> Result:
        result = await views.delete_history(file_id, no_hh)
        return result

    @get("/sing/{file_id: int}", summary="点歌")
    async def song_sing(self, file_id: int, no_hh: models.SessionBase) -> Result:
        result = await views.sing_song(file_id, no_hh)
        return result

    @get("/singHistory/{query_type: str}", summary="点歌历史纪录列表")
    async def history_list(self, query_type: str, no_hh: models.SessionBase) -> Result:
        result = await views.history_list(query_type, no_hh)
        return result

    @get("/setTop/{file_id: int}", summary="置顶")
    async def set_top(self, file_id: int, no_hh: models.SessionBase) -> Result:
        result = await views.set_top(file_id, no_hh)
        return result

    @get("/setSinged/{file_id: int}", summary="设置已经播放过")
    async def set_singed(self, file_id: int, no_hh: models.SessionBase) -> Result:
        result = await views.set_singed(file_id, no_hh)
        return result

    @get("/setSinging/{file_id: str}", summary="设置正在播放")
    async def set_singing(self, file_id: int, no_hh: models.SessionBase) -> Result:
        result = await views.set_singing(file_id, no_hh)
        return result

    @post('/upload/video', summary="上传视频")
    async def upload_file_video(self, data: Request, hh: models.SessionBase) -> Result:
        result = await views.upload_video(data, hh)
        return result

    @get('/deal/video/{file_name: str}', summary="处理视频")
    async def deal_video(self, file_name: str, hh: models.SessionBase) -> Result:
        result = await views.deal_video(file_name, hh)
        return result

    @get('/convert/audio/{file_name: str}', summary="处理音频")
    async def convert_audio(self, file_name: str, hh: models.SessionBase) -> Result:
        result = await views.convert_audio(file_name, hh)
        return result

    @get('/convert/video/{file_name: str}', summary="处理视频")
    async def convert_video(self, file_name: str, hh: models.SessionBase) -> Result:
        result = await views.convert_video(file_name, hh)
        return result

    @get("/events", summary="SSE")
    async def get_events(self, request: Request) -> ServerSentEvent:
        client_queue = asyncio.Queue()
        views.clients.append(client_queue)

        async def event_generator() -> AsyncGenerator[str, None]:
            try:
                while request.is_connected:
                    try:
                        message = await client_queue.get()
                        yield message
                    except:
                        continue
            except:
                logger.error(traceback.format_exc())
            finally:
                views.clients.remove(client_queue)

        return ServerSentEvent(event_generator())

    @get("/send/event", summary="发送数据")
    async def send_event(self, code: int, params: Any) -> Result:
        data = json.dumps({'code': code, 'data': params})
        for client in views.clients:
            await client.put(data)
        return Result()

    @get("/download/{file_name: str}", summary="Download file (获取文件)")
    async def download_file(self, file_name: str, no_hh: models.SessionBase) -> Union[Stream, Result]:
        try:
            file_name = urllib.parse.unquote(file_name)
            file_path = os.path.join(KARAOKE_PATH, file_name)
            file_format = file_name.split('.')[-1]
            headers = {'Accept-Ranges': 'bytes', 'Content-Length': str(os.path.getsize(file_path)),
                       'Content-Disposition': f'inline;filename="{urllib.parse.quote(file_name)}"',
                       'content-type': f'{CONTENT_TYPE.get(file_format, "application/octet-stream")}'}
            return Stream(read_file(file_path), media_type=CONTENT_TYPE.get(file_format, 'application/octet-stream'), headers=headers)
        except:
            logger.error(traceback.format_exc())
            return Result(code=1, msg=Msg.DownloadError.get_text(no_hh.lang))

    @get("/tmp/{file_name: str}", summary="Download Temporary file (获取临时文件)")
    async def download_tmp_file(self, file_name: str, no_hh: models.SessionBase) -> Union[Stream, Result]:
        try:
            file_name = urllib.parse.unquote(file_name)
            file_path = os.path.join(KTV_TMP_PATH, file_name)
            file_format = file_name.split('.')[-1]
            headers = {'Accept-Ranges': 'bytes', 'Content-Length': str(os.path.getsize(file_path)),
                       'Content-Disposition': f'inline;filename="{urllib.parse.quote(file_name)}"',
                       'content-type': f'{CONTENT_TYPE.get(file_format, "application/octet-stream")}'}
            return Stream(read_file(file_path), media_type=CONTENT_TYPE.get(file_format, 'application/octet-stream'), headers=headers)
        except:
            logger.error(traceback.format_exc())
            return Result(code=1, msg=Msg.DownloadError.get_text(no_hh.lang))


# SSE功能对应的消息格式为 {"code": 0, "data": 1}
# code = 0: 无实际含义，可用于心跳检测
# code = 1: 开始/暂停K歌，data = 0 暂停，data = 1 开始，data = 3 已经开始播放，data = 4 已经停止播放，data = 5 第一次播放
# code = 2: 重唱
# code = 3: 切歌，下一首
# code = 4: 切换原唱/伴奏，data = 0 原唱，data = 1 伴奏
# code = 5: 调整原唱音量，data 为音量值
# code = 6: 调整伴奏音量，data 为音量值
# code = 7: 互动，data 为互动方式
# code = 8: 查询已点歌曲列表
