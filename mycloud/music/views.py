#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari
import os
import traceback
import eyed3
from sqlalchemy import asc, desc
from sqlalchemy.exc import NoResultFound
from mycloud import models
from mycloud.database import FileExplorer, Musics
from common.results import Result
from common.messages import Msg
from common.logging import logger
from common.calc import beauty_mp3_time


async def get_mp3_info(file_id: str, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        file = FileExplorer.get_one(file_id)
        mp3_info = eyed3.load(file.full_path)
        result.data = {'id': file.id, 'name': file.name, 'duration': beauty_mp3_time(mp3_info.info.time_secs)}
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file_id, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def get_all_mp3(folder_id: str, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        music_list = FileExplorer.query(parent_id=folder_id, format='mp3').order_by(desc(FileExplorer.id)).all()
        file_list = []
        for f in music_list:
            mp3_info = eyed3.load(f.full_path)
            file_list.append(models.MP3List.from_orm_format(f, beauty_mp3_time(mp3_info.info.time_secs)).model_dump())
        result.data = file_list
        result.total = len(result.data)
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, folder_id, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def get_mp3_history(order_by: str, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        page_size = 200
        if order_by == 'times':
            page_size = 100
        music_list = Musics.query(username=hh.username).order_by(desc(getattr(Musics, order_by))).limit(page_size).all()
        file_list = [models.MusicList.from_orm_format(f).model_dump() for f in music_list]
        result.data = file_list
        result.total = len(result.data)
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def set_mp3_history(query: models.MusicHistory, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        try:
            mp3 = Musics.get_one(query.file_id)
            Musics.update(mp3, times=mp3.times + 1)
        except NoResultFound:
            _ = Musics.create(file_id=query.file_id, name=query.name, singer=query.singer, duration=query.duration, username=hh.username)
        result.msg = Msg.MusicRecord.get_text(hh.lang).format(query.name)
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, query.file_id, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = Msg.Failure.get_text(hh.lang)
        logger.error(traceback.format_exc())
    return result


async def delete_mp3_history(file_id, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        try:
            mp3 = Musics.get_one(file_id=file_id)
            Musics.delete(mp3)
        except NoResultFound:
            pass
        result.msg = f"{Msg.Delete.get_text(hh.lang).format(file_id)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file_id, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Delete.get_text(hh.lang).format(file_id)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def get_mp3_lyric(file_id: str, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        mp3_file = FileExplorer.get_one(file_id)
        lrc_file_name = mp3_file.name.replace('.mp3', '.lrc')
        lrc_file_path = mp3_file.full_path.replace('.mp3', '.lrc')
        if os.path.exists(lrc_file_path):
            with open(lrc_file_path, 'rb') as f:
                result.data = f.read()
            result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
            logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file_id, hh.username, hh.ip))
        else:
            result.code = 1
            result.msg = Msg.FileNotExist.get_text(hh.lang).format(lrc_file_name)
            logger.error(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file_id, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result
