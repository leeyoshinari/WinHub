#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import time
import uuid
import traceback
from litestar import WebSocket
from mycloud.database import ChatRoom, User
from mycloud import models
from settings import WEBRTC_TURN, WEBRTC_STUN, WEBRTC_USER, WEBRTC_CRED
from common.scheduler import scheduler, get_schedule_time
from common.results import Result
from common.logging import logger
from common.messages import Msg


rooms = {}


async def create_code(chat_mode: int, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        room_code = str(uuid.uuid4())[:6]
        ChatRoom.create(code=room_code, mode=chat_mode)
        result.msg = f"{Msg.MeetingCreate.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        result.data = room_code
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, room_code, hh.username, hh.ip))
    except:
        logger.error(traceback.format_exc())
        result.code = 1
        result.msg = f"{Msg.MeetingCreate.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
    return result


async def start_chat(room_code: str, chat_mode: int, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        if room_code not in rooms:
            room = ChatRoom.query(code=room_code, mode=chat_mode, end_time=0).all()
            if not room or len(room) > 1:
                result.code = 1
                result.msg = Msg.FileNotExist.get_text(hh.lang).format(room_code)
                logger.error(Msg.CommonLog1.get_text(hh.lang).format(result.msg, room_code, hh.username, hh.ip))
                return result
            rooms[room_code] = {"users": [], "usernames": {}, "mode": chat_mode}
            room[0].start_time = int(time.time())
            await room[0].save()
        if rooms[room_code]['mode'] != chat_mode:
            result.code = 1
            result.msg = Msg.FileNotExist.get_text(hh.lang).format(room_code)
            logger.error(Msg.CommonLog1.get_text(hh.lang).format(result.msg, room_code, hh.username, hh.ip))
            return result
        rooms[room_code]["usernames"][hh.username] = True
        result.msg = Msg.MeetingJoin.get_text(hh.lang)
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, room_code, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = Msg.Failure.get_text(hh.lang)
        logger.error(traceback.format_exc())
    return result


async def get_stun_server(room_param: str, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        room_code = room_param[:-1]
        chat_mode = int(room_param[-1])
        if room_code not in rooms:
            result.code = 1
            result.msg = Msg.FileNotExist.get_text(hh.lang).format(room_code)
            logger.error(Msg.CommonLog1.get_text(hh.lang).format(result.msg, room_code, hh.username, hh.ip))
            return result
        if hh.username not in rooms[room_code]["usernames"] or not rooms[room_code]["usernames"][hh.username] or rooms[room_code]["mode"] != chat_mode:
            result.code = 1
            result.msg = Msg.AccessPermissionNon.get_text(hh.lang)
            logger.error(Msg.CommonLog1.get_text(hh.lang).format(result.msg, room_code, hh.username, hh.ip))
            return result
        user = User.get_one(hh.username)
        result.data = {'stun': WEBRTC_STUN, 'turn': WEBRTC_TURN, 'user': WEBRTC_USER, 'cred': WEBRTC_CRED, 'username': user.username, 'nickname': user.nickname}
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, room_code, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def delete_code(room_id: int, hh: models.SessionBase) -> Result:
    result = Result()
    try:
        room = ChatRoom.get_one(room_id)
        ChatRoom.delete(room)
        result.msg = f"{Msg.Delete.get_text(hh.lang).format(room.code)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog1.get_text(hh.lang).format(result.msg, room_id, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Delete.get_text(hh.lang).format(room_id)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


async def clear_expire_chat_code():
    try:
        room = ChatRoom.query(start_time=0).all()
        for r in room:
            if time.time() - r.create_time.timestamp() > 172800:
                ChatRoom.delete(r)
                logger.info(f"Delete expire room code for {r.code} successfully.")
    except:
        logger.error(traceback.format_exc())


async def get_room_list(hh: models.SessionBase) -> Result:
    result = Result()
    try:
        room = ChatRoom.all()
        room_list = [models.ChatList.from_orm_format(r, hh.lang).model_dump() for r in room]
        result.data = room_list
        result.total = len(room_list)
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Success.get_text(hh.lang)}"
        logger.info(Msg.CommonLog.get_text(hh.lang).format(result.msg, hh.username, hh.ip))
    except:
        result.code = 1
        result.msg = f"{Msg.Query.get_text(hh.lang)}{Msg.Failure.get_text(hh.lang)}"
        logger.error(traceback.format_exc())
    return result


def is_auth(room_code, websocket: WebSocket, username: str):
    if room_code not in rooms:
        logger.error(Msg.CommonLog1.get_text("en").format(Msg.FileNotExist.get_text("en").format(room_code), room_code, username, ""))
        return False
    if username not in rooms[room_code]["usernames"]:
        logger.error(f"{Msg.AccessPermissionNon.get_text('en')}, MeetingCode: {room_code}, Username: {username}")
        return False
    rooms[room_code]["users"].append(websocket)
    return True


async def leave_room(room_code, websocket: WebSocket, username: str):
    if room_code in rooms:
        rooms[room_code]["users"].remove(websocket)
        del rooms[room_code]["usernames"][username]
        logger.info(f"{Msg.MeetingQuit.get_text('en')}{Msg.Success.get_text('en')}, username: {username}")
        if not rooms[room_code]["users"]:
            room = ChatRoom.query(code=room_code, end_time=0).first()
            del rooms[room_code]
            ChatRoom.update(room, end_time=int(time.time()))
            logger.info(f"Meeting Code: {room_code} is completed ~")


async def broadcast(room_code, message, sender: WebSocket):
    if room_code in rooms:
        for user in rooms[room_code]["users"]:
            if user != sender:
                await user.send_text(message)


scheduler.add_job(clear_expire_chat_code, 'interval', days=1, start_date=get_schedule_time())
