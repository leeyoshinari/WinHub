#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

from fastapi import APIRouter, Depends
from mycloud import models
from mycloud.music import views
from mycloud.auth_middleware import auth


router = APIRouter(prefix='/music', tags=['music (音乐)'], responses={404: {'description': 'Not found'}})


@router.get("/info/get/{file_id}", summary="get music meta info (音乐的信息)")
async def get_music_info(file_id: str, hh: models.SessionBase = Depends(auth)):
    result = await views.get_mp3_info(file_id, hh)
    return result


@router.get("/get/{folder_id}", summary="query music list from folder (从文件夹中查询音乐)")
async def get_music_from_folder(folder_id: str, hh: models.SessionBase = Depends(auth)):
    result = await views.get_all_mp3(folder_id, hh)
    return result


@router.get("/history/get/{flag}", summary="query music history list (查询播放历史列表)")
async def get_music_history_list(flag: int = 1, hh: models.SessionBase = Depends(auth)):
    order_by = '-update_time'
    if flag == 2:
        order_by = '-times'
    result = await views.get_mp3_history(order_by, hh)
    return result


@router.get("/history/delete/{file_id}", summary="delete music history (删除播放历史记录)")
async def delete_music_history(file_id: str, hh: models.SessionBase = Depends(auth)):
    result = await views.delete_mp3_history(file_id, hh)
    return result


@router.post("/record/set", summary="Record playing music (记录播放的音乐)")
async def set_music_record(query: models.MusicHistory, hh: models.SessionBase = Depends(auth)):
    result = await views.set_mp3_history(query, hh)
    return result


@router.get("/lyric/get/{file_id}", summary="query music lyric (根据歌曲查歌词)")
async def get_music_lyric(file_id: str, hh: models.SessionBase = Depends(auth)):
    result = await views.get_mp3_lyric(file_id, hh)
    return result
