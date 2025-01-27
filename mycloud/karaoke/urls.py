#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import os
import json
import asyncio
import traceback
from urllib.parse import unquote
from fastapi import APIRouter, Request, Depends
from sse_starlette import EventSourceResponse
from settings import KARAOKE_PATH, CONTENT_TYPE, KTV_TMP_PATH
from mycloud import models
from mycloud.responses import StreamResponse
from mycloud.auth_middleware import auth, no_auth
from mycloud.karaoke import views
from common.messages import Msg
from common.results import Result
from common.logging import logger


router = APIRouter(prefix='/karaoke', tags=['karaoke (卡拉OK)'], responses={404: {'description': 'Not found'}})


async def read_file(file_path, start_index=0):
    with open(file_path, 'rb') as f:
        f.seek(start_index)
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            yield chunk


@router.on_event('startup')
async def startup_event():
    await views.init_history()


@router.post('/upload', summary="上传歌曲")
async def upload_file(query: Request, hh: models.SessionBase = Depends(auth)):
    result = await views.upload_file(query, hh)
    return result


@router.get("/list", summary="歌曲列表")
async def song_list(q: str = "", page: int = 0, hh: models.SessionBase = Depends(no_auth)):
    result = await views.get_list(q, page, hh)
    return result


@router.get("/delete/{file_id}", summary="删除歌曲")
async def delete_song(file_id: int, hh: models.SessionBase = Depends(auth)):
    result = await views.delete_song(file_id, hh)
    return result


@router.get("/deleteHistory/{file_id}", summary="删除点歌历史记录")
async def delete_history(file_id: int, hh: models.SessionBase = Depends(no_auth)):
    result = await views.delete_history(file_id, hh)
    return result


@router.get("/sing/{file_id}", summary="点歌")
async def song_sing(file_id: int, hh: models.SessionBase = Depends(no_auth)):
    result = await views.sing_song(file_id, hh)
    return result


@router.get("/singHistory/{query_type}", summary="点歌历史纪录列表")
async def history_list(query_type: str, hh: models.SessionBase = Depends(no_auth)):
    result = await views.history_list(query_type, hh)
    return result


@router.get("/setTop/{file_id}", summary="置顶")
async def set_top(file_id: int, hh: models.SessionBase = Depends(no_auth)):
    result = await views.set_top(file_id, hh)
    return result


@router.get("/setSinged/{file_id}", summary="设置已经播放过")
async def set_singed(file_id: int, hh: models.SessionBase = Depends(no_auth)):
    result = await views.set_singed(file_id, hh)
    return result


@router.get("/setSinging/{file_id}", summary="设置正在播放")
async def set_singing(file_id: int, hh: models.SessionBase = Depends(no_auth)):
    result = await views.set_singing(file_id, hh)
    return result


@router.post('/upload/video', summary="上传视频")
async def upload_file_video(query: Request, hh: models.SessionBase = Depends(auth)):
    result = await views.upload_video(query, hh)
    return result


@router.get('/deal/video/{file_name}', summary="处理视频")
async def deal_video(file_name: str, hh: models.SessionBase = Depends(auth)):
    result = await views.deal_video(file_name, hh)
    return result


@router.get('/convert/audio/{file_name}', summary="处理音频")
async def convert_audio(file_name: str, hh: models.SessionBase = Depends(auth)):
    result = await views.convert_audio(file_name, hh)
    return result


@router.get('/convert/video/{file_name}', summary="处理视频")
async def convert_video(file_name: str, hh: models.SessionBase = Depends(auth)):
    result = await views.convert_video(file_name, hh)
    return result


@router.get("/events", summary="SSE")
async def get_events(request: Request):
    client_queue = asyncio.Queue()
    views.clients.append(client_queue)

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                message = await client_queue.get()
                yield message
        except:
            logger.error(traceback.format_exc())
        finally:
            views.clients.remove(client_queue)

    return EventSourceResponse(event_generator())


@router.get("/send/event", summary="发送数据")
async def send_event(code: int, data):
    data = json.dumps({'code': code, 'data': data})
    for client in views.clients:
        await client.put(data)
    return Result()


@router.get("/download/{file_name}", summary="Download file (获取文件)")
async def download_file(file_name: str, hh: models.SessionBase = Depends(no_auth)):
    try:
        file_name = unquote(file_name)
        file_path = os.path.join(KARAOKE_PATH, file_name)
        file_format = file_name.split('.')[-1]
        headers = {'Accept-Ranges': 'bytes', 'Content-Length': str(os.path.getsize(file_path)),
                   'Content-Disposition': f'inline;filename="{file_name}"'}
        return StreamResponse(read_file(file_path), media_type=CONTENT_TYPE.get(file_format, 'application/octet-stream'), headers=headers)
    except:
        logger.error(traceback.format_exc())
        return Result(code=1, msg=Msg.DownloadError.get_text(hh.lang))


@router.get("/tmp/{file_name}", summary="Download Temporary file (获取临时文件)")
async def download_tmp_file(file_name: str, hh: models.SessionBase = Depends(no_auth)):
    try:
        file_name = unquote(file_name)
        file_path = os.path.join(KTV_TMP_PATH, file_name)
        file_format = file_name.split('.')[-1]
        headers = {'Accept-Ranges': 'bytes', 'Content-Length': str(os.path.getsize(file_path)),
                   'Content-Disposition': f'inline;filename="{file_name}"'}
        return StreamResponse(read_file(file_path), media_type=CONTENT_TYPE.get(file_format, 'application/octet-stream'), headers=headers)
    except:
        logger.error(traceback.format_exc())
        return Result(code=1, msg=Msg.DownloadError.get_text(hh.lang))


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
