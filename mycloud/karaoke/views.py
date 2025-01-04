#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import json
import os.path
import asyncio
import subprocess
import traceback
from typing import List
from urllib.parse import unquote
from tortoise.exceptions import DoesNotExist
from mycloud import models
from common.results import Result
from common.messages import Msg
from mycloud.models import Karaoke, KaraokeList, KaraokeHistoryList
from common.logging import logger
from settings import KARAOKE_PATH, KTV_TMP_PATH


clients: List[asyncio.Queue] = []
PAGE_SIZE = 10


async def broadcast_data(data: dict):
    for client in clients[:]:
        try:
            await client.put(json.dumps(data, ensure_ascii=False))
        except:
            logger.error(traceback.format_exc())


async def init_history():
    try:
        songs = await Karaoke.filter(is_sing=-1)
        for s in songs:
            s.is_sing = 1
            await s.save()
    except:
        logger.error(traceback.format_exc())


async def upload_file(query, hh: models.SessionBase) -> Result:

    result = Result()
    query = await query.form()
    file_name = query['file'].filename
    data = query['file'].file
    try:
        file_path = os.path.join(KARAOKE_PATH, file_name)
        song_name = file_name.replace('.mp4', '').replace('_vocals.mp3', '').replace('_accompaniment.mp3', '')
        try:
            file = await Karaoke.get(name=song_name)
        except DoesNotExist:
            file = await Karaoke.create(name=song_name, is_sing=0)
        with open(file_path, 'wb') as f:
            f.write(data.read())
        result.msg = f"{Msg.Upload.get_text(hh.lang).format(file_name)}{Msg.Success.get_text(hh.lang)}"
        result.data = file.name
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Upload.get_text(hh.lang).format(file_name)}{Msg.Failure.get_text(hh.lang)}"
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
        logger.error(traceback.format_exc())
    return result


async def get_list(q: str, page: int, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        if q:
            if page == 0:
                files = await Karaoke.filter(name__contains=q).order_by('-id').offset(0).limit(200)
                total_num = 0
            else:
                files = await Karaoke.filter(name__contains=q).order_by('-id').offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE)
                total_num = await Karaoke.filter(name__contains=q).count()
        else:
            files = await Karaoke.all().order_by('-id').offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE)
            total_num = await Karaoke.all().count()
        file_list = [KaraokeList.from_orm_format(f).model_dump() for f in files]
        result.data = file_list
        result.total = (total_num + PAGE_SIZE - 1) // PAGE_SIZE
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
    return result


async def delete_song(file_id: int, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        file = await Karaoke.get(id=file_id)
        if os.path.exists(f"{KARAOKE_PATH}/{file.name}.mp4"):
            os.remove(f"{KARAOKE_PATH}/{file.name}.mp4")
        if os.path.exists(f"{KARAOKE_PATH}/{file.name}_vocals.mp3"):
            os.remove(f'{KARAOKE_PATH}/{file.name}_vocals.mp3')
        if os.path.exists(f"{KARAOKE_PATH}/{file.name}_accompaniment.mp3"):
            os.remove(f'{KARAOKE_PATH}/{file.name}_accompaniment.mp3')
        await file.delete()
        result.msg = f"{file.name}{Msg.Delete.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file_id, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f"{Msg.Delete.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
    return result


async def delete_history(file_id: int, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        history = await Karaoke.get(id=file_id)
        history.is_sing = 0
        history.times = 0
        history.is_top = 0
        await history.save()
        result.msg = f"{Msg.Delete.get_text(hh.lang).format(f'{history.name}{Msg.HistoryRecords.get_text(hh.lang)}')}{Msg.Success.get_text(hh.lang)}"
        await broadcast_data({"code": 8})
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file_id, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f"{Msg.HistoryRecords.get_text(hh.lang)}{Msg.Delete.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
    return result


async def sing_song(file_id: int, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        msg_list = []
        file = await Karaoke.get(id=file_id)
        if file.status == 0:
            if not os.path.exists(f"{KARAOKE_PATH}/{file.name}.mp4"):
                msg_list.append(Msg.FileNotExist.get_text(hh.lang).format(Msg.File.get_text(hh.lang).format(Msg.Video.get_text(hh.lang))))
            if not os.path.exists(f"{KARAOKE_PATH}/{file.name}_vocals.mp3"):
                msg_list.append(Msg.FileNotExist.get_text(hh.lang).format(Msg.File.get_text(hh.lang).format(Msg.Vocal.get_text(hh.lang))))
            if not os.path.exists(f"{KARAOKE_PATH}/{file.name}_accompaniment.mp3"):
                msg_list.append(Msg.FileNotExist.get_text(hh.lang).format(Msg.File.get_text(hh.lang).format(Msg.Accompaniment.get_text(hh.lang))))
            if len(msg_list) > 0:
                result.code = 1
                result.msg = '，'.join(msg_list)
                logger.warning(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file_id, hh.username, hh.ip))
                return result
            else:
                file.status = 1
        file.is_sing = 1
        file.is_top = 0
        await file.save()
        await broadcast_data({"code": 8})
        result.msg = f"{file.name}{Msg.RequestSong.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file_id, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f"{Msg.RequestSong.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
    return result


async def history_list(query_type: str, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        if query_type == "history":
            songs = await Karaoke.filter(is_sing=2).order_by('-update_time').offset(0).limit(200)
            logger.info(f"{Msg.Query.get_text(hh.lang)}{Msg.HistoryRecords.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}")
        elif query_type == "usually":
            songs = await Karaoke.filter(is_sing=2).order_by('-times').offset(0).limit(200)
            logger.info(f"{Msg.Query.get_text(hh.lang)}{Msg.HistoryRecords.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}")
        elif query_type == "pendingAll":
            songs = await Karaoke.filter(is_sing=-1)
            songs = songs + await Karaoke.filter(is_sing=1, is_top=1).order_by('-update_time')
            songs = songs + await Karaoke.filter(is_sing=1, is_top=0).order_by('update_time')
            logger.info(f"{Msg.Query.get_text(hh.lang)}{Msg.HistoryRecords.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}")
        else:
            songs = await Karaoke.filter(is_sing=-1)
            songs = songs + await Karaoke.filter(is_sing=1, is_top=1).order_by('-update_time')
            songs = songs + await Karaoke.filter(is_sing=1, is_top=0).order_by('update_time').offset(0).limit(4)
            logger.info(f"{Msg.Query.get_text(hh.lang)}{Msg.HistoryRecords.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}")
        song_list = [KaraokeHistoryList.model_validate(f).model_dump() for f in songs]
        result.data = song_list
        result.total = len(result.data)
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.HistoryRecords.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
    return result


async def set_top(file_id: int, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        history = await Karaoke.get(id=file_id)
        history.is_top = 1
        await history.save()
        result.msg = f"{history.name}{Msg.SetTop.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        await broadcast_data({"code": 8})
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file_id, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f"{Msg.SetTop.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
    return result


async def set_singing(file_id: int, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        history = await Karaoke.get(id=file_id)
        history.is_sing = -1
        history.is_top = 0
        await history.save()
        result.msg = Msg.MusicRecord.get_text(hh.lang).format(history.name)
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file_id, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = Msg.VideoError.get_text(hh.lang)
    return result


async def set_singed(file_id: int, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        history = await Karaoke.get(id=file_id)
        history.is_sing = 2
        history.is_top = 0
        history.times = history.times + 1
        await history.save()
        result.msg = f"{history.name}{Msg.Singed.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        await broadcast_data({"code": 8})
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file_id, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f"{Msg.Singed.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
    return result


async def upload_video(query, hh: models.SessionBase) -> Result:
    if not os.path.exists(KTV_TMP_PATH):
        os.mkdir(KTV_TMP_PATH)
    result = Result()
    query = await query.form()
    file_name = query['file'].filename
    data = query['file'].file
    try:
        file_format = file_name.split(".")[-1]
        name = file_name.replace(f".{file_format}", "")
        file_path = os.path.join(KTV_TMP_PATH, f"{name}_origin.{file_format}")
        with open(file_path, 'wb') as f:
            f.write(data.read())
        result.msg = f"{Msg.Upload.get_text(hh.lang).format(file_name)}{Msg.Success.get_text(hh.lang)}"
        result.data = file_name
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file_name, hh.username, hh.ip))
    except:
        result.code = 1
        result.data = file_name
        result.msg = f"{Msg.Upload.get_text(hh.lang).format(file_name)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file_name, hh.username, hh.ip))
        logger.error(traceback.format_exc())
    return result


async def deal_video(file_name: str, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        file_name = unquote(file_name)
        name = file_name.replace(".mp4", "")
        mp4_file = os.path.join(KTV_TMP_PATH, f"{name}_origin.mp4")
        mp3_file = os.path.join(KTV_TMP_PATH, f"{name}.wav")
        cmd1 = ['ffmpeg', '-y', '-i', mp4_file, '-q:a', '0', '-map', 'a', mp3_file]
        subprocess.run(cmd1, check=True)
        no_voice_file = os.path.join(KTV_TMP_PATH, f"{name}_voice.mp4")
        cmd2 = ['ffmpeg', '-y', '-i', mp4_file, '-an', '-vcodec', 'copy', no_voice_file]
        subprocess.run(cmd2, check=True)
        video_file = os.path.join(KTV_TMP_PATH, f"{name}.mp4")
        cmd3 = ['ffmpeg', '-y', '-i', no_voice_file, '-map_metadata', '0', '-c:v', 'copy', '-c:a', 'copy', '-movflags', '+faststart', video_file]
        subprocess.run(cmd3, check=True)
        result.data = {"mp3": f"{name}.wav", "video": f"{name}.mp4"}
        os.remove(no_voice_file)
        result.msg = f"{Msg.Deal.get_text(hh.lang).format(file_name)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file_name, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f"{Msg.Deal.get_text(hh.lang).format(file_name)}{Msg.Failure.get_text(hh.lang)}"
    return result


async def convert_video(file_name: str, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        file_name = unquote(file_name)
        file_format = file_name.split(".")[-1]
        name = file_name.replace(f".{file_format}", "")
        audio_file = os.path.join(KTV_TMP_PATH, f"{name}_origin.{file_format}")
        mp4_file = os.path.join(KTV_TMP_PATH, f"{name}.mp4")
        cmd = ['ffmpeg', '-y', '-i', audio_file, '-c:v', 'libx264', '-c:a', 'aac', mp4_file]
        subprocess.run(cmd, check=True)
        result.data = {"mp4": f"{name}.mp4", "video": f"{name}.{file_format}"}
        result.msg = f"{Msg.Deal.get_text(hh.lang).format(file_name)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file_name, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f"{Msg.Deal.get_text(hh.lang).format(file_name)}{Msg.Failure.get_text(hh.lang)}"
    return result


async def convert_audio(file_name: str, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        file_name = unquote(file_name)
        file_format = file_name.split(".")[-1]
        name = file_name.replace(f".{file_format}", "")
        audio_file = os.path.join(KTV_TMP_PATH, f"{name}_origin.{file_format}")
        mp3_file = os.path.join(KTV_TMP_PATH, f"{name}.mp3")
        cmd = ['ffmpeg', '-y', '-i', audio_file, '-codec:a', 'libmp3lame', mp3_file]
        subprocess.run(cmd, check=True)
        result.data = {"mp3": f"{name}.mp3", "audio": f"{name}.{file_format}"}
        result.msg = f"{Msg.Deal.get_text(hh.lang).format(file_name)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, file_name, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f"{Msg.Deal.get_text(hh.lang).format(file_name)}{Msg.Failure.get_text(hh.lang)}"
    return result
