#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

from litestar import Controller, get, post
from litestar.di import Provide
from mycloud import models
from mycloud.music import views
from mycloud.auth_middleware import auth
from common.results import Result


class MusicController(Controller):
    path = "/music"
    tags = ['music (音乐)']
    dependencies = {"hh": Provide(auth)}

    @get("/info/get/{file_id: str}", summary="get music meta info (音乐的信息)")
    async def get_music_info(self, file_id: str, hh: models.SessionBase) -> Result:
        result = await views.get_mp3_info(file_id, hh)
        return result

    @get("/get/{folder_id: str}", summary="query music list from folder (从文件夹中查询音乐)")
    async def get_music_from_folder(self, folder_id: str, hh: models.SessionBase) -> Result:
        result = await views.get_all_mp3(folder_id, hh)
        return result

    @get("/history/get/{flag: int}", summary="query music history list (查询播放历史列表)")
    async def get_music_history_list(self, flag: int, hh: models.SessionBase) -> Result:
        order_by = 'update_time'
        if flag == 2:
            order_by = 'times'
        result = await views.get_mp3_history(order_by, hh)
        return result

    @get("/history/delete/{file_id: str}", summary="delete music history (删除播放历史记录)")
    async def delete_music_history(self, file_id: str, hh: models.SessionBase) -> Result:
        result = await views.delete_mp3_history(file_id, hh)
        return result

    @post("/record/set", summary="Record playing music (记录播放的音乐)")
    async def set_music_record(self, data: models.MusicHistory, hh: models.SessionBase) -> Result:
        result = await views.set_mp3_history(data, hh)
        return result

    @get("/lyric/get/{file_id: str}", summary="query music lyric (根据歌曲查歌词)")
    async def get_music_lyric(self, file_id: str, hh: models.SessionBase) -> Result:
        result = await views.get_mp3_lyric(file_id, hh)
        return result
