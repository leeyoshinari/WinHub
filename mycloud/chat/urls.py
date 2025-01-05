#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import traceback
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from mycloud import models
from mycloud.auth_middleware import auth
from mycloud.chat import views
from common.logging import logger


router = APIRouter(prefix='/chat', tags=['Chat (音视频聊天)'], responses={404: {'description': 'Not found'}})
rooms = {}


@router.get("/list", summary="Chat records list (聊天记录列表)")
async def chat_list(hh: models.SessionBase = Depends(auth)):
    result = await views.get_room_list(hh)
    return result


@router.get("/create/{chat_mode}", summary="Create code (创建房间码)")
async def create_code(chat_mode: int, hh: models.SessionBase = Depends(auth)):
    result = await views.create_code(chat_mode, hh)
    return result


@router.get("/auth/{chat_mode}/{room_code}", summary="Start Chat (开始聊天)")
async def auth_chat(chat_mode: int, room_code: str, hh: models.SessionBase = Depends(auth)):
    result = await views.start_chat(room_code, chat_mode, hh)
    return result


@router.get("/stun/{room_code}", summary="Get stun & turn (获取stun & turn)")
async def chat_stun(room_code, hh: models.SessionBase = Depends(auth)):
    result = await views.get_stun_server(room_code, hh)
    return result


@router.websocket('/join/{username}/{room_code}')
async def start_chat(websocket: WebSocket, username: str, room_code: str):
    await websocket.accept()
    try:
        if not views.is_auth(room_code, websocket, username):
            await websocket.close()
            return
        while True:
            data = await websocket.receive_text()
            await views.broadcast(room_code, data, websocket)
    except WebSocketDisconnect:
        logger.error("websocket disconnected.")
    except:
        logger.error(traceback.format_exc())
        await websocket.close()
    finally:
        await views.leave_room(room_code, websocket, username)
